import os, time
import threading


class DirScanner:
    def __init__(self, node, path_to_watch):
        self.path_to_watch = path_to_watch
        self.node = node

    def start(self):
        threading.Thread(target=self.scan).start()
        print("directory scanner started")

    def scan(self):
        before = os.listdir(self.path_to_watch)
        if True:
            for item in before:
                try:
                    os.listdir(self.path_to_watch + os.sep + item)
                    scanner = DirScanner(self.node, self.path_to_watch + os.sep + item)
                    threading.Thread(target=scanner.scan).start()
                except NotADirectoryError:
                    self.add(self.path_to_watch + os.sep + item)

        while True:
            time.sleep(10)
            try:
                after = os.listdir(self.path_to_watch)
                added = [f for f in after if f not in before]
                removed = [f for f in before if f not in after]
                if added:
                    for item in added:
                        try:
                            os.listdir(self.path_to_watch + os.sep + item)
                            scanner = DirScanner(self.node, self.path_to_watch + os.sep + item)
                            threading.Thread(target=scanner.scan).start()
                        except NotADirectoryError:
                            self.add(self.path_to_watch + os.sep + item)
                if removed:
                    for item in removed:
                        if '.' in item:
                            self.delete(self.path_to_watch + os.sep + item)

                before = after
            except FileNotFoundError:
                for item in before:
                    if '.' in item:
                        self.delete(self.path_to_watch + os.sep + item)
                break

    def add(self, path):
        print("Added: ", path)
        if not self.node.meta_manager.contains_path(path):
            while True:
                try:
                    self.node.meta_manager.add(path)
                    self.node.sock.sendto(("add|" + self.node.meta_manager.get_md5(path) + "|" + path).encode(),
                                          ('255.255.255.255', self.node.port))
                    break
                except PermissionError:
                    print("file is being written, retrying...")
                    time.sleep(5)


    def delete(self, path):
        print("Removed: ", path)
        if self.node.meta_manager.contains_path(path):
            self.node.meta_manager.remove_path(path)
            self.node.sock.sendto(("del|" + path).encode(), ('255.255.255.255', self.node.port))