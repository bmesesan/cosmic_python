import time
import redis


def main():
    r = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )

    print("PING:", r.ping())

    r.set("wsl:test", "Redis is working from Python")
    print("GET wsl:test:", r.get("wsl:test"))

    r.setex("wsl:expires", 3, "temporary value")
    print("GET wsl:expires:", r.get("wsl:expires"))

    time.sleep(4)
    print("GET wsl:expires after 4s:", r.get("wsl:expires"))

    r.delete("wsl:test")
    print("Done.")


if __name__ == "__main__":
    main()