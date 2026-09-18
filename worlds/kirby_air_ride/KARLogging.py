from CommonClient import CommonContext, logger
from NetUtils import JSONMessagePart, JSONTypes, add_json_text


def _tagged(component: str, text: str) -> str:
    """Prefix a diagnostic line with the subsystem that emitted it."""
    return f"[{component}] {text}"


def log_info(component: str, text: str, *args: object) -> None:
    logger.info(_tagged(component, text), *args)


def log_warning(component: str, text: str, *args: object) -> None:
    logger.warning(_tagged(component, text), *args)


def log_error(component: str, text: str, *args: object) -> None:
    logger.error(_tagged(component, text), *args)


def log_exception(component: str, text: str, *args: object) -> None:
    """log_error plus the traceback of the exception being handled; only valid inside an except block."""
    logger.exception(_tagged(component, text), *args)


def log_color(ctx: CommonContext, text: str, color: str = "white") -> None:
    """Log `text` in `color` to the GUI log, the terminal, and the log file."""
    parts: list[JSONMessagePart] = []
    add_json_text(parts, text, type=JSONTypes.color, color=color)
    ctx.on_print_json({"data": parts, "cmd": "PrintJSON"})


def log_detailed(ctx: CommonContext, component: str, summary: str, detail: str, color: str = "yellow") -> None:
    """Show `summary` to the player and keep `detail`, tagged with `component`, in the log file."""
    log_quiet(component, detail)
    log_color(ctx, summary, color)


def log_toggle(name: str, enabled: bool) -> None:
    """Record an in-game menu toggle in the log file only."""
    log_quiet("Menu", f"{name} toggled {'on' if enabled else 'off'} from in-game menu.")


def log_quiet(component: str, text: str) -> None:
    """Log `text` to the log file only, keeping it out of the terminal and the GUI."""
    logger.info(_tagged(component, text), extra={"NoStream": True, "skip_gui": True})
