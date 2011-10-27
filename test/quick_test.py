import sys
sys.path.insert(0, "..")

from plugin.blueprint import Blueprint

class TestBlueprint(Blueprint):
    class Meta:
        name = 'test_blueprint'
        namespace = 'personal'
        version = (1,0,0)
    # end class BPConfig
# enc class TestBlueprint

TestBlueprint()
    