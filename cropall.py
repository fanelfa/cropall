import cv2
import numpy as np
import fire


class UnionFind:

    def __init__(self):
        self.leader = {}  # maps a member to the group's leader
        self.group = {}  # maps a group leader to the group (which is a set)
        self.label = 1

    def union(self, a, b):
        leadera = self.leader.get(a)
        leaderb = self.leader.get(b)
        if leadera is not None:
            if leaderb is not None:
                if leadera == leaderb:
                    return  # nothing to do
                groupa = self.group[leadera]
                groupb = self.group[leaderb]
                if len(groupa) < len(groupb):
                    a, leadera, groupa, b, leaderb, groupb = b, leaderb, groupb, a, leadera, groupa
                groupa |= groupb
                del self.group[leaderb]
                for k in groupb:
                    self.leader[k] = leadera
            else:
                self.group[leadera].add(b)
                self.leader[b] = leadera
        else:
            if leaderb is not None:
                self.group[leaderb].add(a)
                self.leader[a] = leaderb
            else:
                self.leader[a] = self.leader[b] = a
                self.group[a] = set([a, b])

    def makeLabel(self):
        c = self.label
        self.label += 1
        return c

    def find(self, child):
        hasil = None
        for index in self.group:
            if child in self.group[index]:
                hasil = index
                pass
        return hasil


class CCLabel:
    def __init__(self, imageLocation):
        self.__imageLocation = imageLocation
        self.labels = {}
        self.uf = UnionFind()

    def getLabeledImages(self):
        # fungsi ini akan menghasilkan dictionary array region
        print("Loading ...")

        print("Membuka file gambar ...")
        self.__openImage()

        # cv2.imshow('firstimage', self.image)

        print("Memulai pelabelan gambar ...")
        self.__labeling()

        print("Menyusun gambar ...")
        return self.__makeEachImage()

    def __openImage(self):
        im = cv2.imread(self.__imageLocation, cv2.IMREAD_UNCHANGED)
        self.image = im

    def __labeling(self):
        h = self.image.shape[0]
        w = self.image.shape[1]

        # 4-connectivity
        #
        #   -------------
        #   |   | a |   |
        #   -------------
        #   | b | c |   |
        #   -------------
        #   |   |   |   |
        #   -------------

        # image[x,y] berada di titik c

        color = self.image

        # FIRST PASS
        for y in range(h):
            for x in range(w):

                # jika transparan akan dilewati
                if color[y, x][3] == 0:
                    self.labels[x, y] = None

                #  jika titik b tidak transparan
                #  maka titik c akan diberi label yang sama
                #  dengan titik dengan b
                elif x == 0 and y == 0 and color[y, x][3] > 0:
                    self.labels[x, y] = self.uf.makeLabel()

                elif x > 0 and y == 0 and color[y, x][3] > 0:
                    if color[y, x-1][3] > 0:
                        self.labels[x, y] = self.labels[(x-1, y)]
                    else:
                        self.labels[x, y] = self.uf.makeLabel()

                elif x == 0 and y > 0 and color[y, x][3] == 0:
                    if color[y-1, x][3] > 0:
                        self.labels[x, y] = self.labels[(x, y-1)]
                    else:
                        self.labels[x, y] = self.uf.makeLabel()

                elif color[y, x][3] > 0:
                    if color[y-1, x][3] > 0 and color[y, x-1][3] > 0:
                        if self.labels[(x, y-1)] < self.labels[(x-1, y)]:
                            self.labels[x, y] = self.labels[(x, y-1)]
                            self.uf.union(
                                self.labels[(x-1, y)], self.labels[(x, y-1)])

                        else:
                            self.labels[x, y] = self.labels[(x-1, y)]
                            if self.labels[(x, y-1)] > self.labels[(x-1, y)]:
                                self.uf.union(
                                    self.labels[(x, y-1)], self.labels[(x-1, y)])

                    elif color[y-1, x][3] > 0:
                        self.labels[x, y] = self.labels[(x, y-1)]

                    elif color[y, x-1][3] > 0:
                        self.labels[x, y] = self.labels[(x-1, y)]
                    else:
                        self.labels[x, y] = self.uf.makeLabel()

        # SECOND PASS
        for y in range(h):
            for x in range(w):
                if self.labels[x, y] != None:
                    root = self.uf.find(self.labels[x, y])
                    if root != self.labels[x, y]:
                        self.labels[x, y] = root
                    else:
                        pass
                else:
                    pass

    def __makeEachImage(self):
        dict_image = []
        im = self.image.copy()
        for index in self.uf.group:
            array = [x for x in self.labels if self.labels[x] == index]
            xVal = []
            yVal = []
            for x, y in array:
                xVal.append(x)
                yVal.append(y)
            xMax = max(xVal)
            xMin = min(xVal)
            yMax = max(yVal)
            yMin = min(yVal)
            result = np.zeros([yMax-yMin+2, xMax-xMin+2, 4], dtype=np.uint8)
            dict_image.append(im[yMin:yMax, xMin:xMax])

        return dict_image


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#

def crop(namafile):
    namafile = str(namafile)
    ccl = CCLabel(namafile)

    dicti = ccl.getLabeledImages()

    lenn = len(dicti)
    namafile = namafile.split('.')[0]
    for index in range(lenn):
        print("Menyimpan gambar "+str(index+1)+"/"+str(lenn))
        cv2.imwrite(namafile+'-'+str(index+1)+'.png', dicti[index])


if __name__ == '__main__':
    fire.Fire(crop)
