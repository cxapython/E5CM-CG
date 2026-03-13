import ast
import os
import re
CHINESE_REGEX = re.compile('[\\u4e00-\\u9fff]+')

class Scanner(ast.NodeVisitor):

    def __init__(self):
        self.items = set()

    def visit_FunctionDef(self, node):
        if CHINESE_REGEX.search(node.name):
            self.items.add(('func', node.name))
        self._check_arguments(node.args)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if CHINESE_REGEX.search(node.name):
            self.items.add(('class', node.name))
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) and CHINESE_REGEX.search(node.id):
            self.items.add(('var', node.id))
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        for name in node.names:
            if CHINESE_REGEX.search(name):
                self.items.add(('nonlocal_var', name))
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            if CHINESE_REGEX.search(name):
                self.items.add(('global_var', name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and CHINESE_REGEX.search(node.module):
            self.items.add(('module', node.module))
        for alias in node.names:
            if CHINESE_REGEX.search(alias.name):
                self.items.add(('func', alias.name))
        self.generic_visit(node)

    def _check_arguments(self, args):
        """专门检测函数参数名是否含中文"""
        for arg in args.args:
            if CHINESE_REGEX.search(arg.arg):
                self.items.add(('param', arg.arg))
        for arg in args.kwonlyargs:
            if CHINESE_REGEX.search(arg.arg):
                self.items.add(('param', arg.arg))
        if args.vararg:
            if CHINESE_REGEX.search(args.vararg.arg):
                self.items.add(('param', args.vararg.arg))
        if args.kwarg:
            if CHINESE_REGEX.search(args.kwarg.arg):
                self.items.add(('param', args.kwarg.arg))

def scan():
    s = Scanner()
    for root, _, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.py'):
                try:
                    file_path = os.path.join(root, filename)
                    with open(file_path, encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    s.visit(tree)
                except Exception as e:
                    print(f'扫描文件失败: {file_path} | 错误: {str(e)[:50]}')
                    pass
    return sorted(s.items)
if __name__ == '__main__':
    result = scan()
    print('======== 扫描到的中文标识符 ========')
    for typ, name in result:
        print(f'{typ:12} | {name}')
    with open('chinese_identifiers2.txt', 'w', encoding='utf-8') as f:
        for typ, name in result:
            f.write(f'{typ}\t{name}\n')
    print(f'\n✅ 已导出 {len(result)} 个中文标识符到 chinese_identifiers.txt')