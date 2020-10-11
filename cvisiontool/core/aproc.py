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
from abc import ABC, abstractmethod
from typing import Dict, Any

import numpy as np
import cv2.cv2 as cv

from cvisiontool.core.actions import ActionType, Action


class ActionProcessor:
    def __init__(self):
        self.__processors: Dict[ActionType, AbstractActionStrategy] = {
            ActionType.EROSION: MorphologicalExActionStrategy(),
            ActionType.DILATION: MorphologicalExActionStrategy(),
            ActionType.MORPH_GRADIENT: MorphologicalExActionStrategy(),
            ActionType.MORPH_OPENING: MorphologicalExActionStrategy(),
            ActionType.MORPH_CLOSING: MorphologicalExActionStrategy(),
            ActionType.IN_RANGE: InRangeActionStrategy()
        }

    def process(self, action: Action, mat_bgr: np.ndarray) -> np.ndarray:
        if action.action_type in self.__processors.keys():
            return self.__processors[action.action_type].process(action, mat_bgr)
        else:
            raise ValueError(f'Unknown action: {action.to_string()}')


class AbstractActionStrategy(ABC):
    @abstractmethod
    def process(self, action: Action, mat_bgr: np.ndarray) -> np.ndarray:
        pass

    def _extract_param(self, action: Action, name: str) -> Any:
        if name in action.params.keys():
            return action.params[name]
        else:
            raise ValueError(
                f'Action does not contain param: {name}. Provided action: {action.to_string()}')


class MorphologicalExActionStrategy(AbstractActionStrategy):
    """
        The strategy perform morphological transformation for provided mat.
        Action must contain following params:
            - anchor: int
            - shape: int
                * see supported values in 'self.__supported_shapes'
    """

    def __init__(self):
        self.__supported_shapes = {
            cv.MORPH_RECT: 'Rect',
            cv.MORPH_CROSS: 'Cross',
            cv.MORPH_ELLIPSE: 'Ellipse'
        }

    def process(self, action: Action, mat_bgr: np.ndarray) -> np.ndarray:
        anchor = self._extract_param(action, 'anchor')
        shape = self._extract_param(action, 'shape')
        if action.action_type == ActionType.EROSION:
            morph_type = cv.MORPH_ERODE
        elif action.action_type == ActionType.DILATION:
            morph_type = cv.MORPH_DILATE
        elif action.action_type == ActionType.MORPH_GRADIENT:
            morph_type = cv.MORPH_GRADIENT
        elif action.action_type == ActionType.MORPH_OPENING:
            morph_type = cv.MORPH_OPEN
        elif action.action_type == ActionType.MORPH_CLOSING:
            morph_type = cv.MORPH_CLOSE
        else:
            raise ValueError(f'Current strategy does not support action: {action.to_string()}')

        if shape not in self.__supported_shapes.keys():
            raise ValueError(
                f'"shape" param must have one value of: {json.dumps(self.__supported_shapes)}')
        ksize = 2 * anchor + 1
        element = cv.getStructuringElement(shape,
                                           (ksize, ksize),
                                           (anchor, anchor))
        return cv.morphologyEx(mat_bgr, morph_type, element)


class InRangeActionStrategy(AbstractActionStrategy):
    """
        The strategy performs inRange transformation in provided color space
        Action must contain following parameters:
        - color_space: str
            * see supported values in 'self.__supported_color_spaces'
        - lower_boundary: List[int]
            * list must contain exactly 3 elements
        - upper_boundary: List[int]
            * list must contain exactly 3 elements
    """

    def __init__(self):
        self.__supported_color_spaces = {
            'hsv': cv.COLOR_BGR2HSV
        }

    def process(self, action: Action, mat_bgr: np.ndarray) -> np.ndarray:
        color_space = self._extract_param(action, 'color_space')
        if color_space not in self.__supported_color_spaces.keys():
            raise ValueError(f'Provided color space = {color_space} is not supported')
        lower_boundary = self._extract_param(action, 'lower_boundary')
        if len(lower_boundary) != 3:
            raise ValueError(
                f'"lower_boundary" must be array with 3 int values. Provided value: {lower_boundary}')
        upper_boundary = self._extract_param(action, 'upper_boundary')
        if len(upper_boundary) != 3:
            raise ValueError(
                f'"upper_boundary" must be array with 3 int values. Provided value: {upper_boundary}')

        mat = cv.cvtColor(mat_bgr, self.__supported_color_spaces[color_space])
        return cv.inRange(mat, np.array(lower_boundary), np.array(upper_boundary))
