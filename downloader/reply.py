from cdsapi.api import Result
import time


class Reply:
    # reply from cds server
    __reply: Result

    # current reply state
    __current_result: dict

    def __init__(self, reply: Result):
        if not isinstance(reply, Result):
            raise TypeError('reply must be a cdsapi.api.Result object')

        self.__reply = reply

    @property
    def completed(self) -> bool:
        return self.__current_result["state"] == "completed"

    @property
    def queued(self) -> bool:
        return self.__current_result["state"] in ("queued", "running")

    @property
    def failed(self) -> bool:
        return self.__current_result["state"] in ("failed",)

    def download(self, output_file, refresh_interval: int = 3):
        while True:
            self.__reply.update()
            self.__current_result = self.__reply.reply

            self.__reply.info(
                "Request ID: %s, state: %s" % (self.__current_result["request_id"], self.__current_result["state"]))

            if self.completed:
                break
            elif self.queued:
                self.__reply.info("Request ID: %s, sleep: %s", self.__current_result["request_id"], refresh_interval)
                time.sleep(refresh_interval)
            elif self.failed:
                self.__reply.error("Message: %s", self.__current_result["error"].get("message"))
                self.__reply.error("Reason:  %s", self.__current_result["error"].get("reason"))
                for n in (
                        self.__current_result.get("error", {}).get("context", {}).get("traceback", "").split("\n")
                ):
                    if n.strip() == "":
                        break
                    self.__reply.error("  %s", n)
                raise Exception(
                    "%s. %s." % (self.__current_result["error"].get("message"), self.__current_result["error"].get("reason"))
                )

        self.__reply.download(output_file)
