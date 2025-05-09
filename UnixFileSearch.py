from abc import ABC, abstractmethod
from collections import deque

# ================
# Filter Interface
# ================
class Filter(ABC):
    @abstractmethod
    def apply_filter(self, entity):
        pass


class NameFilter(Filter):
    def __init__(self, name):
        self.name = name

    def apply_filter(self, entity):
        return self.name in entity.get_name()


class SizeFilter(Filter):
    def __init__(self, size):
        self.size = size

    def apply_filter(self, entity):
        return entity.get_size() <= self.size


class ExtensionFilter(Filter):
    def __init__(self, extension):
        self.extension = extension

    def apply_filter(self, entity):
        return entity.get_extension() == self.extension


# =========================
# Composite Filter Operator
# =========================
class CompositeOperator(ABC):
    def __init__(self, filters):
        self.filters = filters

    @abstractmethod
    def apply_operator(self, entity):
        pass


class ANDOperator(CompositeOperator):
    def apply_operator(self, entity):
        return all(filter.apply_filter(entity) for filter in self.filters)


class OROperator(CompositeOperator):
    def apply_operator(self, entity):
        return any(filter.apply_filter(entity) for filter in self.filters)


# ======================
# FileSystem Entity Base
# ======================
class FileSystemEntity:
    def __init__(self, name, size, path):
        self.name = name
        self.size = size
        self.path = path

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def get_extension(self):
        if '.' in self.path:
            return self.path.split('.')[-1]
        return ''


class File(FileSystemEntity):
    def __init__(self, name, size, path):
        super().__init__(name, size, path)


class Directory(FileSystemEntity):
    def __init__(self, name, size, path):
        super().__init__(name, size, path)
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def get_entities(self):
        return self.entities


# ======================
# Unix File Search Tool
# ======================
class UnixFileSearch:
    def __init__(self, root):
        self.root = root

    def search_bfs(self, operator):
        ans = []
        queue = deque([self.root])

        while queue:
            curr_entity = queue.popleft()
            if operator.apply_operator(curr_entity):
                ans.append(curr_entity)

            if isinstance(curr_entity, Directory):
                queue.extend(curr_entity.get_entities())

        return ans

    def search_dfs(self, operator):
        ans = []

        def dfs(curr_entity):
            if operator.apply_operator(curr_entity):
                ans.append(curr_entity)
            if isinstance(curr_entity, Directory):
                for entity in curr_entity.get_entities():
                    dfs(entity)

        dfs(self.root)
        return ans


if __name__ == "__main__":
    # Build file system
    root = Directory("root", 0, "/root")

    file1 = File("readme", 50, "/root/readme.txt")
    file2 = File("code", 100, "/root/code.py")
    file3 = File("notes", 150, "/root/notes.txt")

    subdir = Directory("subdir", 0, "/root/subdir")
    file4 = File("script", 90, "/root/subdir/script.py")
    file5 = File("log", 200, "/root/subdir/log.txt")

    subdir.add_entity(file4)
    subdir.add_entity(file5)

    root.add_entity(file1)
    root.add_entity(file2)
    root.add_entity(file3)
    root.add_entity(subdir)

    # Search setup
    search = UnixFileSearch(root)

    # Filter: Size <= 100
    size_filter = SizeFilter(100)
    print("🔍 Files with size <= 100:")
    for f in search.search_bfs(size_filter):
        print(f" - {f.get_name()} ({f.get_size()}KB)")

    # Filter: Extension = 'py'
    ext_filter = ExtensionFilter("py")
    print("\n🔍 Files with extension .py:")
    for f in search.search_dfs(ext_filter):
        print(f" - {f.get_name()} ({f.get_extension()})")

    # AND Filter: extension == 'py' AND size <= 100
    and_operator = ANDOperator([ext_filter, size_filter])
    print("\n🔍 Files with extension .py AND size <= 100:")
    for f in search.search_dfs(and_operator):
        print(f" - {f.get_name()} ({f.get_extension()}, {f.get_size()}KB)")

    # OR Filter: name contains 'log' OR size <= 100
    name_filter = NameFilter("log")
    or_operator = OROperator([name_filter, size_filter])
    print("\n🔍 Files with name contains 'log' OR size <= 100:")
    for f in search.search_bfs(or_operator):
        print(f" - {f.get_name()} ({f.get_size()}KB)")
