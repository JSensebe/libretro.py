from abc import abstractmethod
from collections.abc import Set
from enum import Enum
from typing import Protocol, runtime_checkable

from libretro.api.av import retro_game_geometry, retro_system_av_info
from libretro.api.proc import retro_proc_address_t
from libretro.api.video import (
    HardwareContext,
    MemoryAccess,
    PixelFormat,
    Rotation,
    retro_framebuffer,
    retro_hw_render_callback,
    retro_hw_render_interface,
)


class FrameBufferSpecial(Enum):
    DUPE = None
    HARDWARE = -1


@runtime_checkable
class VideoDriver(Protocol):
    @abstractmethod
    def refresh(self, data: memoryview | FrameBufferSpecial, width: int, height: int, pitch: int) -> None:
        """
        Updates the framebuffer with the given video data.
        This method is exposed to the core through ``retro_set_video_refresh``.

        :param data: One of the following:

            - A ``memoryview`` pointing to pixel data
              in the format given by ``self.pixel_format``.
              Should be read-only.
            - ``FrameBufferSpecial.DUPE`` if the frontend should re-render the previous frame.
            - ``FrameBufferSpecial.HARDWARE`` if the frontend should render the frame
              using the active hardware context.

        :param width: The width of the frame in ``data``, in pixels.
        :param height: The height of the frame in ``data``, in pixels.
        :param pitch: The width of the frame in ``data``, in bytes.
        :raises TypeError: If any parameter's type is not consistent with this method's signature.
        :raises ValueError: If ``data`` is a ``memoryview``
            and its length is not equal to ``pitch * height``.
        """
        ...

    @property
    @abstractmethod
    def supported_contexts(self) -> Set[HardwareContext]:
        """
        The set of all hardware contexts supported by this driver.
        All video drivers must support at least ``HardwareContext.NONE``,
        which indicates software rendering capabilities.

        Most drivers will only support a single context type,
        but they can support more than one.
        """
        ...

    @property
    @abstractmethod
    def active_context(self) -> HardwareContext:
        """
        The hardware context that is currently exposed to the core.
        Must be a member of ``self.supported_contexts``.

        Will be ``HardwareContext.NONE`` until the core
        successfully requests a hardware context using ``EnvironmentCall.SET_HW_RENDER``,
        at which point it will be set to the requested context type.
        """
        ...

    @property
    @abstractmethod
    def preferred_context(self) -> HardwareContext | None:
        """
        The preferred hardware context for this driver.
        Corresponds to ``EnvironmentCall.GET_PREFERRED_HW_RENDER``.

        Must be a member of ``self.supported_contexts``,
        or ``None`` to indicate that ``EnvironmentCall.GET_PREFERRED_HW_RENDER`` is unavailable.

        Setting or deleting this will not affect the active context.

        :raise NotImplementedError: If attempting to set a preferred context
            that this driver doesn't support.
        :raise TypeError: If attempting to set a non-``HardwareContext`` value.
        """
        ...

    @preferred_context.setter
    @abstractmethod
    def preferred_context(self, context: HardwareContext) -> None:
        ...

    @preferred_context.deleter
    @abstractmethod
    def preferred_context(self) -> None:
        ...

    @abstractmethod
    def set_context(self, callback: retro_hw_render_callback) -> retro_hw_render_callback | None:
        """
        Corresponds to ``EnvironmentCall.SET_HW_RENDER``.

        :param callback:
        :raises TypeError: If ``callback`` is not a ``retro_hw_render_callback``.
        :return: If the request in ``callback`` is accepted, a new ``retro_hw_render_callback``
          with values and pointers that the core can use to interact with the hardware context.
          Otherwise, ``None``.
        """
        ...

    @abstractmethod
    def context_reset(self) -> None:
        """
        Initializes the hardware context
        and calls the core's registered ``context_reset`` callback.
        """
        ...

    @abstractmethod
    def context_destroy(self) -> None:
        """
        Destroys the hardware context
        and calls the core's registered ``retro_hw_render_callback.context_destroy`` callback.
        """
        ...

    @property
    @abstractmethod
    def rotation(self) -> Rotation:
        """
        Get the rotation of the video output.

        If the video driver doesn't support rotation,
        then this property should return ``Rotation.NONE``.

        :raise UnsupportedEnvCall: If setting a rotation
          and this driver doesn't support ``EnvironmentCall.SET_ROTATION``.
        """
        ...

    @rotation.setter
    @abstractmethod
    def rotation(self, rotation: Rotation) -> None:
        ...

    @property
    @abstractmethod
    def can_dupe(self) -> bool:
        """
        Whether the frontend can re-render the previous frame.

        :note: Drivers may override this property to give it a setter.

        :raises UnsupportedEnvCall: If this driver doesn't support ``EnvironmentCall.CAN_DUPE``.
        """
        ...

    @property
    @abstractmethod
    def pixel_format(self) -> PixelFormat:
        """
        The pixel format that this driver uses for the frame buffer.

        :raise ValueError: If trying to set an invalid ``PixelFormat``.
        :raise UnsupportedEnvCall: If this driver doesn't support ``EnvironmentCall.SET_PIXEL_FORMAT``.
        """
        ...

    @pixel_format.setter
    @abstractmethod
    def pixel_format(self, format: PixelFormat) -> None:
        ...

    @abstractmethod
    def get_hw_framebuffer(self) -> int:
        ...

    @abstractmethod
    def get_proc_address(self, sym: bytes) -> retro_proc_address_t | None:
        ...

    @property
    @abstractmethod
    def system_av_info(self) -> retro_system_av_info | None:
        ...

    @system_av_info.setter
    @abstractmethod
    def system_av_info(self, av_info: retro_system_av_info) -> None:
        ...

    @property
    @abstractmethod
    def geometry(self) -> retro_game_geometry:
        ...

    @geometry.setter
    @abstractmethod
    def geometry(self, geometry: retro_game_geometry) -> None:
        ...

    @abstractmethod
    def get_software_framebuffer(
        self, width: int, height: int, flags: MemoryAccess
    ) -> retro_framebuffer | None:
        ...

    @property
    @abstractmethod
    def hw_render_interface(self) -> retro_hw_render_interface | None:
        ...

    @property
    @abstractmethod
    def shared_context(self) -> bool:
        ...

    @shared_context.setter
    @abstractmethod
    def shared_context(self, value: bool) -> None:
        ...

    @property
    @abstractmethod
    def frame(self):
        ...

    @property
    @abstractmethod
    def frame_max(self):
        ...


__all__ = [
    "VideoDriver",
    "FrameBufferSpecial",
]
