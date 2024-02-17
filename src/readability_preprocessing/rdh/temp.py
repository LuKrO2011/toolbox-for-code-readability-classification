class RemComController:
    def __init__(self):
        self.arr = []
        self.comment = "//"
        self.esc = "\\"
        self.bcopen = "/*"
        self.bcclose = "*/"
        self.comcheck = True
        self.esccheck = True
        self.bccheck = True

    def split(self):
        full = self.appText
        finaltext = ""

        # Remove block comments
        if self.bccheck and self.bcopen != '':
            finaltext = self.remove_block_comments(finaltext, full)
        else:
            finaltext = full

        # Remove line comments
        if self.comcheck and self.comment != '':
            finaltext = self.remove_line_comments(finaltext)

        # Remove extra newlines
        finaltext = finaltext.replace('\n\n\n', '\n\n').lstrip('\n')

        self.appText = ''
        self.arr = []
        self.appText = finaltext

    def remove_line_comments(self, finaltext):
        lines = finaltext.split('\n')
        for line in lines:
            rem = line
            if self.esc == '':
                self.esc = None

            if self.comment in line:
                comIndexes = [i for i in range(len(line)) if line.startswith(
                    self.comment, i)]

                d, s = 0, 0
                for i in range(len(line)):
                    if line[i] == '"' and (
                        not self.esccheck or self.esc == '' or line[i - len(
                        self.esc):i] != self.esc
                        or (line[i - len(self.esc):i] == self.esc and line[
                                                                      i - 2 * len(
                                                                          self.esc):i - len(
                                                                          self.esc)] == self.esc)) and d == 0 and s == 0:
                        d += 1
                    elif line[i] == '"' and (
                        not self.esccheck or self.esc == '' or line[i - len(
                        self.esc):i] != self.esc
                        or (line[i - len(self.esc):i] == self.esc and line[
                                                                      i - 2 * len(
                                                                          self.esc):i - len(
                                                                          self.esc)] == self.esc)) and d == 1 and s == 0:
                        d -= 1
                    if line[i] == "'" and (
                        not self.esccheck or self.esc == '' or line[i - len(
                        self.esc):i] != self.esc
                        or (line[i - len(self.esc):i] == self.esc and line[
                                                                      i - 2 * len(
                                                                          self.esc):i - len(
                                                                          self.esc)] == self.esc)) and d == 0 and s == 0:
                        s += 1
                    elif line[i] == "'" and (
                        not self.esccheck or self.esc == '' or line[i - len(
                        self.esc):i] != self.esc
                        or (line[i - len(self.esc):i] == self.esc and line[
                                                                      i - 2 * len(
                                                                          self.esc):i - len(
                                                                          self.esc)] == self.esc)) and d == 0 and s == 1:
                        s -= 1

                    if i in comIndexes and d == 0 and s == 0:
                        rem = line[:i]
                        break

            if not rem.strip():
                rem = '\n'
            self.arr.append(rem)
        finaltext = '\n'.join(self.arr)
        return finaltext

    def remove_block_comments(self, finaltext, full):
        bcOpenIndexes, bcCloseIndexes = [], []
        o, c = -1, -1
        while (o := full.find(self.bcopen, o + 1)) != -1:
            bcOpenIndexes.append(o)
        if self.bcclose != '':
            while (c := full.find(self.bcclose, c + 1)) != -1:
                bcCloseIndexes.append(c)
        d, s, bc, record = 0, 0, 0, 0
        for i in range(len(full)):
            if full[i] == '"' and (not self.esccheck or self.esc == '' or full[
                                                                          i - len(
                                                                              self.esc):i] != self.esc
                                   or (full[
                                       i - len(self.esc):i] == self.esc and full[
                                                                            i - 2 * len(
                                                                                self.esc):i - len(
                                                                                self.esc)] == self.esc)) and d == 0 and s == 0:
                d += 1
            elif full[i] == '"' and (not self.esccheck or self.esc == '' or full[
                                                                            i - len(
                                                                                self.esc):i] != self.esc
                                     or (full[
                                         i - len(self.esc):i] == self.esc and full[
                                                                              i - 2 * len(
                                                                                  self.esc):i - len(
                                                                                  self.esc)] == self.esc)) and d == 1 and s == 0:
                d -= 1
            if full[i] == "'" and (not self.esccheck or self.esc == '' or full[
                                                                          i - len(
                                                                              self.esc):i] != self.esc
                                   or (full[
                                       i - len(self.esc):i] == self.esc and full[
                                                                            i - 2 * len(
                                                                                self.esc):i - len(
                                                                                self.esc)] == self.esc)) and d == 0 and s == 0:
                if i not in bcOpenIndexes:
                    s += 1
            elif full[i] == "'" and (not self.esccheck or self.esc == '' or full[
                                                                            i - len(
                                                                                self.esc):i] != self.esc
                                     or (full[
                                         i - len(self.esc):i] == self.esc and full[
                                                                              i - 2 * len(
                                                                                  self.esc):i - len(
                                                                                  self.esc)] == self.esc)) and d == 0 and s == 1:
                if i not in bcCloseIndexes:
                    s -= 1
            elif full[i] == '\n':
                d = 0
                s = 0

            if i in bcOpenIndexes and d == 0 and s == 0 and bc == 0:
                finaltext += full[record:i]
                i += len(self.bcopen) - 1
                bc = 1
            elif self.bcclose != '' and i in bcCloseIndexes and bc == 1:
                record = i + len(self.bcclose)
                i += len(self.bcclose) - 1
                bc = 0
            elif i == len(full) - 1 and bc == 0:
                finaltext += full[record:]
        return finaltext
