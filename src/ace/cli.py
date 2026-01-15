import argparse
import logging

from ace.logging_config import configure_logging

logger= logging.getLogger(__name__)


def main() -> None:
    parser= argparse.ArgumentParser(prog="ace", description="Autonomous Cognitive Engine (ACE)")
    parser.add_argument("--log-level", default=None, help="DEBUG/INFO/WARNING/ERROR")
    args=parser.parse_args()

    configure_logging(args.log_level or "INFO")
    logger.info("ACE CLI ready.")