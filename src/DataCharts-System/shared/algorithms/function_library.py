"""
函数库定义

包含系统支持的所有数学函数、统计函数、数据变换函数和滤波函数
"""

import numpy as np
import pandas as pd
import scipy.ndimage
from typing import Dict, List, Any, Callable


class FunctionLibrary:
    """函数库管理类"""
    
    # 数学函数
    MATH_FUNCTIONS = {
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'log': np.log,
        'exp': np.exp,
        'sqrt': np.sqrt,
        'abs': np.abs,
        'floor': np.floor,
        'ceil': np.ceil,
        'round': np.round,
        'pi': np.pi,
        'e': np.e
    }
    
    # 统计函数
    STATISTICAL_FUNCTIONS = {
        'mean': np.mean,
        'std': np.std,
        'var': np.var,
        'median': np.median,
        'min': np.min,
        'max': np.max,
        'sum': np.sum,
        'count': len,
        'quantile': lambda x, q: np.quantile(x, q)
    }
    
    # 数据变换函数
    TRANSFORM_FUNCTIONS = {
        'normalize': lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) if np.max(x) != np.min(x) else x,
        'standardize': lambda x: (x - np.mean(x)) / np.std(x) if np.std(x) != 0 else x,
        'scale': lambda x, factor=1: x * factor,
        'log_transform': lambda x: np.log(np.where(x > 0, x, 1)),
        'power_transform': lambda x, power=2: np.power(x, power)
    }
    
    # 滤波函数
    FILTER_FUNCTIONS = {
        'moving_average': lambda x, window=5: pd.Series(x).rolling(window=window, center=True).mean().fillna(method='bfill').fillna(method='ffill'),
        'gaussian_filter': lambda x, sigma=1: scipy.ndimage.gaussian_filter1d(x, sigma),
        'median_filter': lambda x, size=3: scipy.ndimage.median_filter(x, size=size),
        'rolling_sum': lambda x, window=5: pd.Series(x).rolling(window=window).sum().fillna(0)
    }
    
    @classmethod
    def get_all_functions(cls) -> Dict[str, Callable]:
        """
        获取所有可用函数
        
        Returns:
            Dict[str, Callable]: 函数名到函数对象的映射
        """
        all_functions = {}
        all_functions.update(cls.MATH_FUNCTIONS)
        all_functions.update(cls.STATISTICAL_FUNCTIONS)
        all_functions.update(cls.TRANSFORM_FUNCTIONS)
        all_functions.update(cls.FILTER_FUNCTIONS)
        return all_functions
    
    @classmethod
    def get_function_categories(cls) -> Dict[str, List[str]]:
        """
        获取函数分类信息
        
        Returns:
            Dict[str, List[str]]: 分类名到函数列表的映射
        """
        return {
            '数学函数': list(cls.MATH_FUNCTIONS.keys()),
            '统计函数': list(cls.STATISTICAL_FUNCTIONS.keys()),
            '数据变换': list(cls.TRANSFORM_FUNCTIONS.keys()),
            '滤波函数': list(cls.FILTER_FUNCTIONS.keys())
        }
    
    @classmethod
    def get_supported_function_names(cls) -> List[str]:
        """
        获取所有支持的函数名列表
        
        Returns:
            List[str]: 支持的函数名列表
        """
        return list(cls.get_all_functions().keys())
    
    @classmethod
    def is_function_supported(cls, func_name: str) -> bool:
        """
        检查函数是否被支持
        
        Args:
            func_name: 函数名
            
        Returns:
            bool: 是否支持该函数
        """
        return func_name in cls.get_supported_function_names()
    
    @classmethod
    def get_function(cls, func_name: str) -> Callable:
        """
        根据函数名获取函数对象
        
        Args:
            func_name: 函数名
            
        Returns:
            Callable: 函数对象
            
        Raises:
            KeyError: 函数不存在时抛出
        """
        all_functions = cls.get_all_functions()
        if func_name not in all_functions:
            raise KeyError(f"不支持的函数: {func_name}")
        return all_functions[func_name]
    
    @classmethod
    def get_function_info(cls, func_name: str) -> Dict[str, Any]:
        """
        获取函数信息
        
        Args:
            func_name: 函数名
            
        Returns:
            Dict[str, Any]: 函数信息
        """
        # 确定函数类别
        category = None
        for cat_name, func_list in cls.get_function_categories().items():
            if func_name in func_list:
                category = cat_name
                break
        
        # 获取函数文档
        func = cls.get_function(func_name)
        doc = getattr(func, '__doc__', '无文档说明')
        
        return {
            'name': func_name,
            'category': category,
            'documentation': doc,
            'is_available': True
        }
    
    @classmethod
    def validate_function_usage(cls, func_name: str, args: List[Any]) -> bool:
        """
        验证函数使用是否正确
        
        Args:
            func_name: 函数名
            args: 参数列表
            
        Returns:
            bool: 是否可以正确使用
        """
        try:
            if not cls.is_function_supported(func_name):
                return False
            
            # 基础参数检查
            if func_name in ['moving_average', 'gaussian_filter', 'median_filter', 'rolling_sum']:
                # 这些函数需要至少一个参数
                return len(args) >= 1
            elif func_name in ['scale', 'power_transform', 'quantile']:
                # 这些函数可能需要额外参数
                return len(args) >= 1
            else:
                # 大多数函数只需要一个数据参数
                return len(args) >= 1
                
        except Exception:
            return False
