import dataclasses


@dataclasses.dataclass
class License:
    short_name: str
    proper_name: str
    badge_url: str
    link: str


# https://gist.github.com/lukas-h/2a5d00690736b4c3a7ba

LICENSES = {
    "agpl_v3": License(
        short_name="agpl_v3",
        proper_name="AGPL v3",
        badge_url="https://img.shields.io/badge/License-AGPL_v3-blue.svg",
        link="https://www.gnu.org/licenses/agpl-3.0",
    ),
    "apache_v2": License(
        short_name="apache_v2",
        proper_name="Apache 2.0",
        badge_url="https://img.shields.io/badge/License-Apache_2.0-blue.svg",
        link="https://opensource.org/licenses/Apache-2.0",
    ),
    "bsd2": License(
        short_name="bsd2",
        proper_name="BSD 2-Clause",
        badge_url="https://img.shields.io/badge/License-BSD_2--Clause-orange.svg",
        link="https://opensource.org/licenses/BSD-2-Clause",
    ),
    "bsd3": License(
        short_name="bsd3",
        proper_name="BSD 3-Clause",
        badge_url="https://img.shields.io/badge/License-BSD_3--Clause-blue.svg",
        link="https://opensource.org/licenses/BSD-3-Clause",
    ),
    "gpl_v2": License(
        short_name="gpl_v2",
        proper_name="GPL v2",
        badge_url="https://img.shields.io/badge/License-GPL_v2-blue.svg",
        link="https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html",
    ),
    "gpl_v3": License(
        short_name="gpl_v3",
        proper_name="GPL v3",
        badge_url="https://img.shields.io/badge/License-GPL_v3-blue.svg",
        link="https://www.gnu.org/licenses/gpl-3.0",
    ),
    "lgpl_v3": License(
        short_name="lgpl_v3",
        proper_name="LGPL v3",
        badge_url="https://img.shields.io/badge/License-LGPL_v3-blue.svg",
        link="https://www.gnu.org/licenses/lgpl-3.0",
    ),
    "mit": License(
        short_name="mit",
        proper_name="MIT",
        badge_url="https://img.shields.io/badge/License-MIT-yellow.svg",
        link="https://opensource.org/licenses/MIT",
    ),
    "mozilla_v2": License(
        short_name="mozilla_v2",
        proper_name="MPL 2.0",
        badge_url="https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg",
        link="https://opensource.org/licenses/MPL-2.0",
    ),
}
