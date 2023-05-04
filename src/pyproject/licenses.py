import dataclasses


@dataclasses.dataclass
class License:
    short_name: str
    proper_name: str
    badge_url: str
    link: str


LICENSES = {
    "apache": License(
        short_name="apache",
        proper_name="Apache",
        badge_url="https://img.shields.io/badge/License-Apache_2.0-blue.svg",
        link="https://opensource.org/licenses/Apache-2.0",
    ),
    "bsd3": License(
        short_name="bsd3",
        proper_name="BSD 3-Clause",
        badge_url="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg",
        link="https://opensource.org/licenses/BSD-3-Clause",
    ),
    "gpl_v3": License(
        short_name="gpl_v3",
        proper_name="GPL v3",
        badge_url="https://img.shields.io/badge/License-GPLv3-blue.svg",
        link="https://www.gnu.org/licenses/gpl-3.0",
    ),
    "mit": License(
        short_name="mit",
        proper_name="MIT",
        badge_url="https://img.shields.io/badge/License-MIT-yellow.svg",
        link="https://opensource.org/licenses/MIT",
    ),
}
