"""Bounded capture entrypoints in the official Epic registry."""
import toolset_registry
from toolset_registry.registration import Registration
import unreal as u
import layout03_capture as capture

@u.uclass()
class OpeningLobbyLayout03CaptureTools(u.ToolsetDefinition):
    """Capture matched and gameplay-FOV live PIE frames."""

    @toolset_registry.tool_call
    @staticmethod
    def action(operation: str, view: str) -> str:
        """Operations prepare, restore, camera, shoot and lighting; named C1/C2/C3 views only."""
        if operation == 'lighting':
            return capture.lighting()
        if operation == 'prepare':
            return capture.prepare()
        if operation == 'restore':
            return capture.restore()
        if operation == 'camera':
            return capture.capture(view)
        if operation == 'shoot':
            return capture.shoot(view)
        raise ValueError(operation)

registration = Registration([OpeningLobbyLayout03CaptureTools])
registration.register()
