#   cvisiontool - the software for exploring Computer Vision
#   Copyright (C) 2020 pendyurinandrey
#  #
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
import json
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List


class ActionType(Enum):
    EROSION = 'erosion'
    DILATION = 'dilation'
    MORPH_GRADIENT = 'morphological_gradient'
    MORPH_OPENING = 'morphological_opening'
    MORPH_CLOSING = 'morphological_closing'
    IN_RANGE = 'in_range'


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    params: Dict[str, Any]

    def to_string(self) -> str:
        return f'Action: {self.action_type.name}, params: [{json.dumps(self.params)}]'

    def to_json(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'params': self.params
        }


class ActionFactory(ABC):
    @staticmethod
    def create_erosion_action(shape: int, anchor: int) -> Action:
        return Action(ActionType.EROSION, {
            'shape': shape,
            'anchor': anchor
        })

    @staticmethod
    def create_dilation_action(shape: int, anchor: int) -> Action:
        return Action(ActionType.DILATION, {
            'shape': shape,
            'anchor': anchor
        })

    @staticmethod
    def create_morph_gradient_action(shape: int, anchor: int) -> Action:
        return Action(ActionType.MORPH_GRADIENT, {
            'shape': shape,
            'anchor': anchor
        })

    @staticmethod
    def create_morph_opening_action(shape: int, anchor: int):
        return Action(ActionType.MORPH_OPENING, {
            'shape': shape,
            'anchor': anchor
        })

    @staticmethod
    def create_morph_closing_action(shape: int, anchor: int):
        return Action(ActionType.MORPH_CLOSING, {
            'shape': shape,
            'anchor': anchor
        })

    @staticmethod
    def create_in_range_action(color_space: str, lower_boundary: List[int],
                               upper_boundary: List[int]):
        return Action(ActionType.IN_RANGE, {
            'color_space': color_space,
            'lower_boundary': lower_boundary,
            'upper_boundary': upper_boundary
        })


