"""Base controller for Eufy Clean devices."""
from typing import Dict, Optional, Union, Any
from ..constants.devices import EUFY_CLEAN_X_SERIES
from ..constants.state import WorkMode, Control
from ...lib.utils import decode, encode, get_multi_data, get_proto_file

class Base:
    def __init__(self, config: Dict[str, Any]):
        """Initialize base controller.

        Args:
            config: Configuration dictionary containing device settings
        """
        self.device_id: str = config.get('device_id', '')
        self.device_model: str = config.get('device_model', '')
        self.config = config
        self.debug_log = config.get('debug', False)
        self.robovac_data: Dict = {}
        self.novel_api = False
        self.dps_map: Dict = {}

    async def get_robovac_data(self) -> Dict:
        """Get current robovac data."""
        return self.robovac_data

    async def get_clean_speed(self) -> str:
        """Get current clean speed."""
        if isinstance(self.robovac_data.get('CLEAN_SPEED'), (int, str)) or len(self.robovac_data.get('CLEAN_SPEED', [])) == 1:
            from ...eufy_clean.constants.state import EUFY_CLEAN_NOVEL_CLEAN_SPEED
            clean_speeds = [str(speed) for speed in EUFY_CLEAN_NOVEL_CLEAN_SPEED]
            return clean_speeds[int(self.robovac_data['CLEAN_SPEED'])].lower()

        return str(self.robovac_data.get('CLEAN_SPEED', '')).lower() or 'standard'

    async def get_control_response(self) -> Optional[Dict]:
        """Get control response."""
        try:
            if self.novel_api:
                value = await decode('control.proto', 'ModeCtrlResponse', self.robovac_data['PLAY_PAUSE'])
                print('152 - control response', value)
                return value or {}
            return None
        except Exception:
            return {}

    async def get_play_pause(self) -> bool:
        """Get play/pause state."""
        return bool(self.robovac_data.get('PLAY_PAUSE', False))

    async def get_work_mode(self) -> str:
        """Get current work mode."""
        try:
            if self.novel_api:
                values = await get_multi_data('work_status.proto', 'WorkStatus', self.robovac_data['WORK_MODE'])
                mode = next((v for v in values if v['key'] == 'Mode'), None)
                return str(mode.get('value', '')).lower() if mode else 'auto'
            return str(self.robovac_data.get('WORK_MODE', '')).lower()
        except Exception:
            return 'auto'

    async def get_battery_level(self) -> int:
        """Get current battery level."""
        return int(self.robovac_data.get('BATTERY_LEVEL', 0))

    async def get_error_code(self) -> Union[str, int]:
        """Get current error code."""
        try:
            if self.novel_api:
                value = await decode('error_code.proto', 'ErrorCode', self.robovac_data['ERROR_CODE'])
                if value and value.get('warn'):
                    return value['warn'][0]
                return 0
            return self.robovac_data.get('ERROR_CODE', 0)
        except Exception as error:
            print(error)
            return 0

    async def set_clean_speed(self, clean_speed: str) -> None:
        """Set clean speed.

        Args:
            clean_speed: Speed setting to apply
        """
        try:
            if self.novel_api:
                from ...eufy_clean.constants.state import EUFY_CLEAN_NOVEL_CLEAN_SPEED
                clean_speeds = [str(speed) for speed in EUFY_CLEAN_NOVEL_CLEAN_SPEED]
                set_clean_speed = clean_speeds.index(clean_speed)
                print('Setting clean speed to: ', set_clean_speed, clean_speeds, clean_speed)
                await self.send_command({
                    self.dps_map['CLEAN_SPEED']: set_clean_speed
                })
            else:
                print('Setting clean speed to: ', clean_speed)
                await self.send_command({
                    self.dps_map['CLEAN_SPEED']: clean_speed
                })
        except Exception as error:
            print(error)

    async def auto_clean(self) -> None:
        """Start auto cleaning."""
        value = True

        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'autoClean': {
                    'cleanTimes': 1
                }
            })
            return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

        await self.send_command({self.dps_map['WORK_MODE']: WorkMode.AUTO})
        return await self.play()

    async def scene_clean(self, scene_id: int) -> None:
        """Start scene cleaning.

        Args:
            scene_id: Scene ID to clean
        """
        await self.stop()

        value = True
        increment = 3  # Scene 1 is 4, Scene 2 is 5, Scene 3 is 6 etc.

        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.START_SCENE_CLEAN,
                'sceneClean': {
                    'sceneId': scene_id + increment
                }
            })

        return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

    async def play(self) -> None:
        """Resume cleaning."""
        value = True

        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.RESUME_TASK
            })

        return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

    async def pause(self) -> None:
        """Pause cleaning."""
        value = False

        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.PAUSE_TASK
            })

        return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

    async def stop(self) -> None:
        """Stop cleaning."""
        value = False

        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.STOP_TASK
            })

        return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

    async def go_home(self) -> None:
        """Send robot back to charging dock."""
        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.START_GOHOME
            })
            return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

        return await self.send_command({self.dps_map['GO_HOME']: True})

    async def spot_clean(self) -> None:
        """Start spot cleaning."""
        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.START_SPOT_CLEAN
            })
            return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

    async def room_clean(self) -> None:
        """Start room cleaning."""
        if self.novel_api:
            value = await encode('control.proto', 'ModeCtrlRequest', {
                'method': Control.START_SELECT_ROOMS_CLEAN
            })
            return await self.send_command({self.dps_map['PLAY_PAUSE']: value})

        if self.device_model in EUFY_CLEAN_X_SERIES:
            await self.send_command({self.dps_map['WORK_MODE']: WorkMode.SMALL_ROOM})
            return await self.play()

        await self.send_command({self.dps_map['WORK_MODE']: WorkMode.ROOM})
        return await self.play()

    async def set_clean_param(self, config: Dict[str, str]) -> None:
        """Set cleaning parameters.

        Args:
            config: Dictionary containing clean parameters
                Possible keys:
                - clean_type: 'SWEEP_AND_MOP' | 'SWEEP_ONLY' | 'MOP_ONLY'
                - mop_mode: 'HIGH' | 'MEDIUM' | 'LOW'
                - clean_extent: 'NORMAL' | 'NARROW' | 'QUICK'
        """
        if not self.novel_api:
            return

        clean_param_proto = await get_proto_file('clean_param.proto')
        clean_params = {
            'cleanType': clean_param_proto.lookup_type('CleanType').Value,
            'cleanExtent': clean_param_proto.lookup_type('CleanExtent').Value,
            'mopMode': clean_param_proto.lookup_type('MopMode').Level,
        }

        is_mop = config.get('clean_type') in ['SWEEP_AND_MOP', 'MOP_ONLY']

        request_params = {
            'cleanParam': {
                'cleanType': {'value': clean_params['cleanType'][config['clean_type']]} if config.get('clean_type') else {},
                'cleanExtent': {'value': clean_params['cleanExtent'][config['clean_extent']]} if config.get('clean_extent') else {},
                'mopMode': {'level': clean_params['mopMode'][config['mop_mode']]} if config.get('mop_mode') and is_mop else {},
                'smartModeSw': {},
                'cleanTimes': 1
            }
        }

        print('setCleanParam - requestParams', request_params)

        value = await encode('clean_param.proto', 'CleanParamRequest', request_params)
        await self.send_command({self.dps_map['CLEANING_PARAMETERS']: value})
