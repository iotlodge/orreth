# PROVENANCE: Fable 5 (claude-fable-5) — 0019 demo, the spectator site · 2026-07-06
"""Orreth.ai spectator demo — a captured moment of the universe, served static.

Deliberately the smallest possible surface: S3 (private, OAC) + CloudFront.
No compute, no login, no origin to probe — the strongest form of "view only"
is a site that cannot act. Mirrors the jsbarth.com CDK idioms (tags, price
class, DNS-validated ACM) minus the EC2 origin it doesn't need.

Custom domain is optional: pass -c demo_domain=demo.orreth.ai
-c orreth_zone_id=ZXXXX to alias it; without them the CloudFront URL serves.
"""
from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    Tags,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct


class OrrethDemoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *,
                 site_dir: str, demo_domain: str | None = None,
                 zone_id: str | None = None, zone_name: str | None = None,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Tags.of(self).add("Project", "orreth.ai")
        Tags.of(self).add("ManagedBy", "CDK")

        bucket = s3.Bucket(
            self,
            "SiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        cert = None
        hosted_zone = None
        if demo_domain and zone_id and zone_name:
            hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
                self, "Zone", zone_name=zone_name, hosted_zone_id=zone_id)
            cert = acm.Certificate(
                self,
                "SiteCert",
                domain_name=demo_domain,
                validation=acm.CertificateValidation.from_dns(hosted_zone),
            )

        distribution = cloudfront.Distribution(
            self,
            "CDN",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            domain_names=[demo_domain] if cert else None,
            certificate=cert,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            http_version=cloudfront.HttpVersion.HTTP2_AND_3,
        )

        if hosted_zone and demo_domain:
            route53.ARecord(
                self,
                "DemoAlias",
                zone=hosted_zone,
                record_name=demo_domain,
                target=route53.RecordTarget.from_alias(
                    targets.CloudFrontTarget(distribution)),
            )

        # ship the captured moment; every deploy invalidates the edge cache.
        # /deeds/ and /media/ are published to the bucket out-of-band (the 0042
        # publish door, campaign videos) — excluded so prune never eats them.
        s3deploy.BucketDeployment(
            self,
            "DeploySite",
            sources=[s3deploy.Source.asset(site_dir)],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
            exclude=["deeds/*", "media/*"],
        )

        CfnOutput(self, "CloudFrontDomain", value=distribution.distribution_domain_name)
        CfnOutput(self, "CloudFrontDistId", value=distribution.distribution_id)
        if demo_domain:
            CfnOutput(self, "DemoUrl", value=f"https://{demo_domain}")
