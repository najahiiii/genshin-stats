import argparse
import asyncio
import logging
import os
import pathlib

import genshin
import jinja2

logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument("-t",
                    "--template",
                    default="src/template.html",
                    type=pathlib.Path)
parser.add_argument("-o",
                    "--output",
                    default="output/stats.html",
                    type=pathlib.Path)
parser.add_argument("-C", "--cookies", default=None)
parser.add_argument("-c",
                    "--claim",
                    default=False,
                    action=argparse.BooleanOptionalAction)
parser.add_argument("-V",
                    "--verbose",
                    default=False,
                    action=argparse.BooleanOptionalAction)
parser.add_argument("-l",
                    "--lang",
                    "--language",
                    choices=genshin.LANGS,
                    default="en-us")


async def main():
    args = parser.parse_args()
    cookies = args.cookies or os.environ["COOKIES"]
    debug = args.verbose

    client = genshin.Client(cookies, debug=debug, game=genshin.Game.GENSHIN)
    user = await client.get_full_genshin_user(0, lang=args.lang)

    abyss = user.abyss.current if user.abyss.current.floors else user.abyss.previous

    diary = await client.get_diary()

    if args.claim:
        try:
            await client.claim_daily_reward(lang=args.lang, reward=False)
        except genshin.AlreadyClaimed:
            pass
        except Exception as e:
            print(f"Could not claim daily rewards: \"{e}\"")
        finally:
            reward = await client.claimed_rewards(lang=args.lang).next()
            reward_info = await client.get_reward_info()
    else:
        reward = await client.claimed_rewards(lang=args.lang).next()
        reward_info = await client.get_reward_info()

    template = jinja2.Template(args.template.read_text())
    rendered = template.render(
        user=user,
        lang=args.lang,
        abyss=abyss,
        reward=reward,
        diary=diary,
        reward_info=reward_info,
    )
    args.output.write_text(rendered)


if __name__ == "__main__":
    asyncio.run(main())
