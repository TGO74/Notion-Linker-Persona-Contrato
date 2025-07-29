#!/usr/bin/env python3
"""
Tests para funciones críticas del Notion Linker
Ejecutar con: python test_functions.py
"""

import sys
import os

# Agregar el directorio actual al path para importar las funciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_clean_name():
    """Test para la función clean_name"""
    print("🧪 Probando función clean_name...")
    
    # Importar la función desde main.py
    from main import clean_name
    
    # Casos de prueba
    test_cases = [
        ("Juan Pérez", "JUAN PEREZ"),
        ("María José", "MARIA JOSE"),
        ("José María", "JOSE MARIA"),
        ("Ángela López", "ANGELA LOPEZ"),
        ("José Luis", "JOSE LUIS"),
        ("", ""),
        ("   Juan   ", "JUAN"),
        ("juan pérez", "JUAN PEREZ"),
        ("JUAN PEREZ", "JUAN PEREZ"),  # Ya está limpio
        ("María-José", "MARIA-JOSE"),
        ("José María (Jr.)", "JOSE MARIA (JR.)"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_name, expected in test_cases:
        result = clean_name(input_name)
        if result == expected:
            print(f"✅ '{input_name}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ '{input_name}' -> '{result}' (esperado: '{expected}')")
    
    print(f"\n📊 Resultado: {passed}/{total} tests pasaron")
    return passed == total

def test_extract_property_value():
    """Test para la función extract_property_value"""
    print("\n🧪 Probando función extract_property_value...")
    
    # Importar la función desde main.py
    from main import extract_property_value
    
    # Casos de prueba
    test_cases = [
        # rich_text
        (
            {"nombre": {"type": "rich_text", "rich_text": [{"plain_text": "Juan Pérez"}]}},
            "nombre",
            "Juan Pérez"
        ),
        # title
        (
            {"nombre": {"type": "title", "title": [{"plain_text": "María José"}]}},
            "nombre",
            "María José"
        ),
        # select
        (
            {"estado": {"type": "select", "select": {"name": "Activo"}}},
            "estado",
            "Activo"
        ),
        # multi_select
        (
            {"tags": {"type": "multi_select", "multi_select": [{"name": "Urgente"}]}},
            "tags",
            "Urgente"
        ),
        # formula
        (
            {"formula": {"type": "formula", "formula": {"string": "Calculado"}}},
            "formula",
            "Calculado"
        ),
        # propiedad vacía
        (
            {"nombre": {"type": "rich_text", "rich_text": []}},
            "nombre",
            ""
        ),
        # propiedad inexistente
        (
            {"nombre": {"type": "rich_text", "rich_text": [{"plain_text": "Test"}]}},
            "inexistente",
            ""
        ),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for properties, property_name, expected in test_cases:
        result = extract_property_value(properties, property_name)
        if result == expected:
            print(f"✅ '{property_name}' -> '{result}'")
            passed += 1
        else:
            print(f"❌ '{property_name}' -> '{result}' (esperado: '{expected}')")
    
    print(f"\n📊 Resultado: {passed}/{total} tests pasaron")
    return passed == total

def test_environment_validation():
    """Test para validación de entorno"""
    print("\n🧪 Probando validación de entorno...")
    
    # Importar la función desde main.py
    from main import validate_environment
    
    # Simular variables de entorno
    original_env = os.environ.copy()
    
    # Test 1: Sin variables de entorno
    os.environ.clear()
    result1 = validate_environment()
    print(f"✅ Sin variables: {result1} (esperado: False)")
    
    # Test 2: Con variables completas
    os.environ.update({
        "NOTION_API_KEY": "test_key",
        "CONTRATOS_DB_ID": "test_contratos",
        "PERSONAS_DB_ID": "test_personas"
    })
    result2 = validate_environment()
    print(f"✅ Con variables: {result2} (esperado: True)")
    
    # Restaurar entorno original
    os.environ.clear()
    os.environ.update(original_env)
    
    return not result1 and result2

def run_all_tests():
    """Ejecuta todos los tests"""
    print("🚀 Iniciando tests del Notion Linker...\n")
    
    tests = [
        ("clean_name", test_clean_name),
        ("extract_property_value", test_extract_property_value),
        ("environment_validation", test_environment_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ Test '{test_name}' PASÓ\n")
            else:
                print(f"❌ Test '{test_name}' FALLÓ\n")
        except Exception as e:
            print(f"💥 Test '{test_name}' ERROR: {e}\n")
    
    print("=" * 50)
    print(f"📊 RESULTADO FINAL: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron!")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 