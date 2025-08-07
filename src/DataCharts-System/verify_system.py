#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ç³»ç»ŸéªŒè¯è„šæœ¬

éªŒè¯DataChartsç³»ç»Ÿçš„å®Œæ•´åŠŸèƒ½
"""

import requests
import time
import concurrent.futures
import json


def test_health_check():
    """æµ‹è¯•å¥åº·æ£€æŸ¥"""
    try:
        r = requests.get('http://127.0.0.1:8000/health', timeout=10)
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, str(e)


def test_system_info():
    """æµ‹è¯•ç³»ç»Ÿä¿¡æ¯"""
    try:
        r = requests.get('http://127.0.0.1:8000/api/system/info', timeout=10)
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, str(e)


def test_function_library():
    """æµ‹è¯•å‡½æ•°åº“"""
    try:
        r = requests.get('http://127.0.0.1:8000/api/function/library', timeout=10)
        data = r.json()
        return r.status_code == 200, len(data.get('supported_functions', {}))
    except Exception as e:
        return False, str(e)


def test_chart_types():
    """æµ‹è¯•å›¾è¡¨ç±»å‹"""
    try:
        r = requests.get('http://127.0.0.1:8000/api/chart/types', timeout=10)
        data = r.json()
        return r.status_code == 200, data.get('chart_types', {})
    except Exception as e:
        return False, str(e)


def test_data_upload():
    """æµ‹è¯•æ•°æ®ä¸Šä¼ """
    try:
        # åˆ›å»ºæµ‹è¯•æ•°æ®
        test_data = "x,y,category\n1,2,A\n2,4,B\n3,6,A\n4,8,B\n5,10,A"
        
        # æ¨¡æ‹Ÿæ–‡ä»¶ä¸Šä¼ 
        files = {'file': ('test.csv', test_data, 'text/csv')}
        r = requests.post('http://127.0.0.1:8000/api/data/upload', files=files, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            return True, data.get('data_id', 'Unknown')
        else:
            return False, f"Status: {r.status_code}"
    except Exception as e:
        return False, str(e)


def test_function_parse():
    """æµ‹è¯•å‡½æ•°è§£æ"""
    try:
        payload = {'expression': 'mean(x) + std(y)'}
        r = requests.post(
            'http://127.0.0.1:8000/api/function/parse',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return True, data.get('is_valid', False)
        else:
            return False, f"Status: {r.status_code}"
    except Exception as e:
        return False, str(e)


def test_chart_creation():
    """æµ‹è¯•å›¾è¡¨åˆ›å»º"""
    try:
        payload = {
            'data_id': 'test_data_id',
            'chart_type': 'line',
            'config': {
                'title': 'éªŒè¯æµ‹è¯•å›¾è¡¨',
                'x_axis': 'Xè½´',
                'y_axis': 'Yè½´',
                'width': 800,
                'height': 600
            }
        }
        r = requests.post(
            'http://127.0.0.1:8000/api/chart/create',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return True, data.get('chart_id', 'Unknown')
        else:
            return False, f"Status: {r.status_code}"
    except Exception as e:
        return False, str(e)


def test_concurrent_requests():
    """æµ‹è¯•å¹¶å‘è¯·æ±‚"""
    def make_request():
        try:
            r = requests.get('http://127.0.0.1:8000/health', timeout=5)
            return r.status_code
        except:
            return 0
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]
    end_time = time.time()
    
    success_count = sum(1 for r in results if r == 200)
    total_time = end_time - start_time
    success_rate = success_count / len(results) * 100
    
    return success_rate >= 90, {
        'total_time': round(total_time, 3),
        'success_rate': round(success_rate, 1),
        'successful_requests': success_count,
        'total_requests': len(results)
    }


def run_verification():
    """è¿è¡Œå®Œæ•´éªŒè¯"""
    print("ğŸš€ å¼€å§‹DataChartsç³»ç»ŸéªŒè¯...")
    print("=" * 50)
    
    tests = [
        ("å¥åº·æ£€æŸ¥", test_health_check),
        ("ç³»ç»Ÿä¿¡æ¯", test_system_info),
        ("å‡½æ•°åº“", test_function_library),
        ("å›¾è¡¨ç±»å‹", test_chart_types),
        ("æ•°æ®ä¸Šä¼ ", test_data_upload),
        ("å‡½æ•°è§£æ", test_function_parse),
        ("å›¾è¡¨åˆ›å»º", test_chart_creation),
        ("å¹¶å‘æ€§èƒ½", test_concurrent_requests),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"ğŸ“‹ æµ‹è¯• {test_name}...", end=" ")
        try:
            success, data = test_func()
            if success:
                print("âœ… é€šè¿‡")
                results[test_name] = {"status": "PASS", "data": data}
                passed += 1
            else:
                print("âŒ å¤±è´¥")
                results[test_name] = {"status": "FAIL", "error": data}
        except Exception as e:
            print("âŒ å¼‚å¸¸")
            results[test_name] = {"status": "ERROR", "error": str(e)}
    
    print("=" * 50)
    print(f"ğŸ¯ éªŒè¯å®Œæˆ: {passed}/{total} æµ‹è¯•é€šè¿‡")
    
    if passed == total:
        print("ğŸ‰ æ‰€æœ‰æµ‹è¯•é€šè¿‡ï¼DataChartsç³»ç»Ÿå®Œå…¨æ­£å¸¸è¿è¡Œï¼")
        return True
    else:
        print("âš ï¸  éƒ¨åˆ†æµ‹è¯•å¤±è´¥ï¼Œè¯·æ£€æŸ¥ç³»ç»Ÿé…ç½®")
        for test_name, result in results.items():
            if result["status"] != "PASS":
                print(f"   - {test_name}: {result.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    success = run_verification()
    if success:
        print("\nâœ… ç³»ç»ŸéªŒè¯æˆåŠŸå®Œæˆï¼")
    else:
        print("\nâŒ ç³»ç»ŸéªŒè¯å‘ç°é—®é¢˜ï¼")