# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import sys
from types import TracebackType
from typing import Any, Optional

from omegaconf import DictConfig

import hydra
from hydra.utils import UNSAFE_DISABLE_EXECUTION_CHECKS, instantiate


def fail() -> None:
    raise ValueError("target failed")


def fail_nested() -> None:
    instantiate(
        {"_target_": "my_app.fail"},
        _execution_whitelist_=UNSAFE_DISABLE_EXECUTION_CHECKS,
    )


@hydra.main(config_path=None, config_name=None)
def my_app(cfg: DictConfig) -> Any:
    if cfg.case == "hook":

        def hook(
            error_type: type[BaseException],
            error: BaseException,
            tb: Optional[TracebackType],
        ) -> None:
            print(f"hook: {error_type.__name__}", file=sys.stderr)
            while tb is not None:
                print(f"frame: {tb.tb_frame.f_code.co_name}", file=sys.stderr)
                tb = tb.tb_next
            cause = error.__cause__
            if cause is not None:
                print(f"cause: {type(cause).__name__}: {cause}", file=sys.stderr)
                cause_tb = cause.__traceback__
                while cause_tb is not None:
                    print(
                        f"cause frame: {cause_tb.tb_frame.f_code.co_name}",
                        file=sys.stderr,
                    )
                    cause_tb = cause_tb.tb_next

        sys.excepthook = hook

    if cfg.case in {"target", "hook"}:
        return instantiate(
            {"_target_": "my_app.fail"},
            _execution_whitelist_=UNSAFE_DISABLE_EXECUTION_CHECKS,
        )
    if cfg.case == "invalid":
        return instantiate({"_target_": 123})
    if cfg.case == "nested":
        return instantiate(
            {"_target_": "my_app.fail_nested"},
            _execution_whitelist_=UNSAFE_DISABLE_EXECUTION_CHECKS,
        )
    return instantiate({"child": {"_target_": "__main__.missing"}})


if __name__ == "__main__":
    my_app()
