import ast
import os
import json
from copy import deepcopy
with open('/Users/chennan/Downloads/E5CM-CG/rename_3.json', 'r', encoding='utf-8') as f:
    REPLACE_MAP = json.load(f)

class PythonRenamer(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        node.name = REPLACE_MAP.get(node.name, node.name)
        self._rename_arguments(node.args)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        node.name = REPLACE_MAP.get(node.name, node.name)
        self._rename_arguments(node.args)
        self.generic_visit(node)
        return node

    def _rename_arguments(self, args):
        """批量重命名函数参数（位置参数/关键字参数/可变参数）"""
        for arg in args.args:
            arg.arg = REPLACE_MAP.get(arg.arg, arg.arg)
        for arg in args.kwonlyargs:
            arg.arg = REPLACE_MAP.get(arg.arg, arg.arg)
        if args.vararg:
            args.vararg.arg = REPLACE_MAP.get(args.vararg.arg, args.vararg.arg)
        if args.kwarg:
            args.kwarg.arg = REPLACE_MAP.get(args.kwarg.arg, args.kwarg.arg)
        for arg in args.posonlyargs:
            arg.arg = REPLACE_MAP.get(arg.arg, arg.arg)

    def visit_Global(self, node):
        node.names = [REPLACE_MAP.get(name, name) for name in node.names]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        node.name = REPLACE_MAP.get(node.name, node.name)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        node.id = REPLACE_MAP.get(node.id, node.id)
        return node

    def visit_ImportFrom(self, node):
        if node.module:
            node.module = REPLACE_MAP.get(node.module, node.module)
        for alias in node.names:
            alias.name = REPLACE_MAP.get(alias.name, alias.name)
        return node

    def visit_Attribute(self, node):
        node.attr = REPLACE_MAP.get(node.attr, node.attr)
        self.generic_visit(node)
        return node

    def visit_Nonlocal(self, node):
        node.names = [REPLACE_MAP.get(name, name) for name in node.names]
        self.generic_visit(node)
        return node

    def visit_Import(self, node):
        for alias in node.names:
            alias.name = REPLACE_MAP.get(alias.name, alias.name)
            if alias.asname:
                alias.asname = REPLACE_MAP.get(alias.asname, alias.asname)
        return node

    def visit_Decorator(self, node):
        self.generic_visit(node)
        return node

    def visit_NamedExpr(self, node):
        if isinstance(node.target, ast.Name):
            node.target.id = REPLACE_MAP.get(node.target.id, node.target.id)
        self.generic_visit(node)
        return node

def process_py(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        new_tree = PythonRenamer().visit(tree)
        new_code = ast.unparse(new_tree)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f'✅ PY替换完成: {filepath}')
    except Exception as e:
        print(f'❌ PY处理失败: {filepath} | 错误: {str(e)[:50]}')

def recursive_rename_json(obj):
    """递归替换JSON字典/列表中的所有key"""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            new_k = REPLACE_MAP.get(k, k)
            new_dict[new_k] = recursive_rename_json(v)
        return new_dict
    elif isinstance(obj, list):
        return [recursive_rename_json(item) for item in obj]
    else:
        return obj

def process_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        new_json_data = recursive_rename_json(deepcopy(json_data))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_json_data, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        print(f'✅ JSON替换完成: {filepath}')
    except Exception as e:
        print(f'❌ JSON处理失败: {filepath} | 错误: {str(e)[:50]}')

def main(root_path='.'):
    for root, _, files in os.walk(root_path):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.py'):
                process_py(filepath)
            elif file.endswith('.json'):
                process_json(filepath)
    print('\n🎉 所有文件处理完成！请检查项目运行状态。')
if __name__ == '__main__':
    main()