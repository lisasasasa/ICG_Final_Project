#! python3
import os
import cv2
import sys
import numpy as np
import util
import importlib
import gc
#from google.colab.patches import cv2_imshow
#importlib.reload(util)
print("which color do you want")
print("red,orange,grass_green,bright_green,green_and_blue,blue,purple,pink")
Type = input()
colorType = {
    "red":{"alpha":0,"Templates":[(0,0.16)]},
    "orange":{"alpha":0,"Templates":[(0.08,0.08)]},
    "grass_green":{"alpha":0,"Templates":[(0.25,0.16)]},
    "bright_green":{"alpha":0,"Templates":[(0.33,0.16)]},
    "green_and_blue":{"alpha":0,"Templates":[(0.5,0.16)]},
    "blue":{"alpha":0,"Templates":[(0.58,0.16)]},
    "purple":{"alpha":0,"Templates":[(0.75,0.16)]},
    "pink":{"alpha":0,"Templates":[(0.83,0.16)]}
}
'''
colorType = {
    "red":{"alpha":0,"Templates":[(0,0.1)]},
    "orange":{"alpha":36,"Templates":[(0,0.1)]},
    "yellow":{"alpha":72,"Templates":[(0,0.1)]},
    "grass_green":{"alpha":108,"Templates":[(0,0.1)]}
}
'''
HueTemplates = {
    "i"       : [( 0.00, 0.05)],
    "V"       : [( 0.00, 0.26)],
    "L"       : [( 0.00, 0.05), ( 0.25, 0.22)],
    "mirror_L": [( 0.00, 0.05), (-0.25, 0.22)],
    "I"       : [( 0.00, 0.05), ( 0.50, 0.05)],
    "T"       : [( 0.25, 0.50)],
    "Y"       : [( 0.00, 0.26), ( 0.50, 0.05)],
    "X"       : [( 0.00, 0.26), ( 0.50, 0.26)],
    "SET"      : colorType[Type]["Templates"]
}
template_types = list(HueTemplates.keys())
M = len(template_types)
A = 360

deg_distance = util.deg_distance

class HueSector:

    def __init__(self, center, width):
        # In Degree [0,2 pi)
        self.center = center
        self.width  = width
        self.border = [(self.center - self.width/2), (self.center + self.width/2)]

    def is_in_sector(self, H):
        # True/False matrix if hue resides in the sector
        return deg_distance(H, self.center) < self.width/2

    def distance_to_border(self, H):     
        #H_1 = deg_distance(H, self.border[0])
        #H_2 = deg_distance(H, self.border[1])
        d1 = np.abs(H - self.border[0])
        d2 = np.abs(360-d1)
        H_1 = np.minimum(d1, d2)
        del d1,d2
        gc.collect()
        d1 = np.abs(H - self.border[1])
        d2 = np.abs(360-d1)
        H_2 = np.minimum(d1, d2)
        del d1,d2
        gc.collect()
        H_dist2bdr = np.minimum(H_1, H_2)
        del H_1,H_2
        gc.collect()
        
        return H_dist2bdr
        
    def closest_border(self, H):
        H_1 = deg_distance(H, self.border[0])
        H_2 = deg_distance(H, self.border[1])
        H_cls_bdr = np.argmin((H_1, H_2), axis=0)
        H_cls_bdr = 2*(H_cls_bdr - 0.5)
        return H_cls_bdr


    def closest_border_dir(self, H):
        H_1 = deg_distance(H, self.border[0])
        H_2 = deg_distance(H, self.border[1])
        H_cls_bdr = np.argmin((H_1, H_2), axis=0)
        H_dir = np.zeros(H.shape)
        for i in range(2):
            mask = (H_cls_bdr == i)
            H_dir += util.deg_closest_direction(H, self.border[i]) * mask
        return H_dir

    def distance_to_center(self, H):
        H_dist2ctr = deg_distance(H, self.center)
        return H_dist2ctr

class HarmonicScheme:

    def __init__(self, m, alpha):
        self.m = m
        self.alpha = alpha
        self.reset_sectors()

    def reset_sectors(self):
        self.sectors = []
        for t in HueTemplates[self.m]:
            center = t[0] * 360 + self.alpha
            width  = t[1] * 360
            sector = HueSector(center, width)
            self.sectors.append( sector )
   

    def harmony_score(self, X):
        # Opencv store H as [0, 180) --> [0, 360)
        H = X[:, :, 0].astype(np.int32)* 2
        # Opencv store S as [0, 255] --> [0, 1]
        S = X[:, :, 1].astype(np.float32) / 255.0
        
        H_dis = self.hue_distance(H)
        H_dis = np.deg2rad(H_dis)
        return np.sum( np.multiply(H_dis, S) )

    def hue_distance(self, H):
        H_dis = []
        for i in range(len(self.sectors)):
            sector = self.sectors[i]
            H_dis.append(sector.distance_to_border(H))
            H_dis[i][sector.is_in_sector(H)] = 0
        H_dis = np.asarray(H_dis)        
        H_dis = H_dis.min(axis=0)
        return H_dis

    def hue_shifted(self, X, num_superpixels=-1):
        Y = X.copy()
        print(X.shape)
        H = X[:, :, 0].astype(np.int32)*2
        '''
        for sector in self.sectors:
            print(sector.distance_to_border(H))
            print(sector.distance_to_border(H).type)
        '''    
        H_d2b = [ sector.distance_to_border(H) for sector in self.sectors ]
        H_d2b = np.asarray(H_d2b)
        #S = X[:, :, 1].astype(np.float32) / 255.0
        
        H_cls = np.argmin(H_d2b, axis=0)
        del H_d2b
        gc.collect()
        if num_superpixels != -1:
            SEEDS = cv2.ximgproc.createSuperpixelSEEDS(X.shape[1], X.shape[0], X.shape[2], num_superpixels, 10)
            SEEDS.iterate(X, 4)

            '''
            contour = SEEDS.getLabelContourMask()
            for y in range(HSV_image.shape[0]):
                for x in range(HSV_image.shape[1]):
                    if contour[y,x] == 255:
                        color_image[y,x,0] = 255
                        color_image[y,x,1] = 255
                        color_image[y,x,2] = 255
            cv2.imwrite("seeds.jpg", color_image)
            '''
            V = np.zeros(H.shape).reshape(-1)
            N = V.shape[0]
            del V
            gc.collect()
            H_ctr = np.zeros((H.shape))
            grid_num = SEEDS.getNumberOfSuperpixels()
            labels = SEEDS.getLabels()
            '''
            for l in range(grid_num):

                e = np.zeros(len(self.sectors))

                H_P = H[labels==l]
                S_P = S[labels==l]
                
                H_V_P = H_P.copy()
                for i in range(len(self.sectors)):
                    sector = self.sectors[i]
                    mask = (H_cls == i)
                    H_ctr[mask] = sector.center
                    H_V_P = H_ctr[labels==l]
                

                    d = util.deg_distance(H_P, H_V_P)
        
                    tmp = np.multiply(d, s)
                    e[i] = np.sum(tmp)
                
                if e[0] < e[1]:
                    H_cls[labels==i] = 0
                else:
                    H_cls[labels==i] = s
            '''
            for i in range(grid_num):

                P = [ [], [] ]
                s = np.average(H_cls[labels==i])
                #print(i, s)
                if s > 0.5:
                    s = 1
                else:
                    s = 0
                H_cls[labels==i] = s

        H_ctr = np.zeros((H.shape))
        H_wid = np.zeros((H.shape))
        H_d2c = np.zeros((H.shape))
        H_dir = np.zeros((H.shape))
        
        for i in range(len(self.sectors)):
            sector = self.sectors[i]
            mask = (H_cls == i)
            H_ctr[mask] = sector.center
            H_wid[mask] = sector.width
            H_dir += sector.closest_border(H) * mask
            H_dist2ctr = sector.distance_to_center(H)
            #H_dist2ctr[sector.is_in_sector(H)] = 0
            H_d2c += H_dist2ctr * mask
            
        H_sgm = H_wid / 2
        H_gau = util.normalized_gaussian(H_d2c, 0, H_sgm)
        H_tmp = np.multiply(H_wid / 2, 1 - H_gau)
        H_shf = np.multiply( H_dir, H_tmp )
        H_new = (H_ctr + H_shf).astype(np.int32)

        for i in range(len(self.sectors)):
            sector = self.sectors[i]
            mask = sector.is_in_sector(H)
            np.copyto(H_new, H, where=sector.is_in_sector(H))
        #H_new = tmp.data

        H_new = np.remainder(H_new, 360)
        H_new = (H_new/2).astype(np.uint8)
        print(H_new.shape)
        Y[:,:,0] = H_new
        return Y

    def energy_E(self, X, V, P):
        w1 = 1.0
        w2 = 1.0
        e = w1 * self.energy_E1(X, V, P)# + w2 * self.energy_E2(X, V, p)
        return e

    def energy_E1(self, X, V, P):
        # Opencv store H as [0, 180) --> [0, 360)
        H = X[:, :, 0].astype(np.int32)* 2
        # Opencv store S as [0, 255] --> [0, 1]
        S = X[:, :, 1].astype(np.float32) / 255.0
        
        H_P = H[ P[0], P[1] ]
        V_P = V[ P[0], P[1] ]
        S_P = S[ P[0], P[1] ]

        d = util.deg_distance(H_P, V_P)
        s = S_P
        
        e1 = np.multiply(d, s)
        e1 = np.sum(e1)
        return e1

    def energy_E2(self, X, V, P):
        # Opencv store H as [0, 180) --> [0, 360)
        H = X[:, :, 0].astype(np.int32)* 2
        # Opencv store S as [0, 255] --> [0, 1]
        S = X[:, :, 1].astype(np.float32) / 255.0

        P_set, Q_set = PQ_N4(X, P)

        V_P = V[ P_set[0], P_set[1] ]
        V_Q = V[ Q_set[0], Q_set[1] ]
        S_P = S[ P_set[0], P_set[1] ]
        S_Q = S[ Q_set[0], Q_set[1] ]
        H_P = H[ P_set[0], P_set[1] ]
        H_Q = H[ Q_set[0], Q_set[1] ]
        
        delta = util.delta( V_p, V_q )
        s_max = np.max((S_P, S_Q), axis=0)
        d = util.deg_distance(H_P, H_Q)
        
        e2 = np.multiply( np.multiply( delta, s_max ), np.reciprocal(d) )
        e2 = np.sum(e2)
        return e2

    def update_alpha(self, alpha):
        self.alpha = alpha
        self.sectors = []
        for t in HueTemplates[self.m]:
            center = t[0] * 360 + alpha
            width  = t[1] * 360
            sector = HueSector(center, width)
            self.sectors.append( sector )

    def update_template(self, m):
        self.m = m
        self.sectors = []
        for t in HueTemplates[m]:
            center = t[0] * 360 + self.alpha
            width  = t[1] * 360
            sector = HueSector(center, width)
            self.sectors.append( sector )

def B(X):
    '''
    F_matrix = np.zeros((M, A))
    for i in range(M):
        m = template_types[i]
        for j in range(A):
            alpha = 360/A * j
            print(i,j)
            harmomic_scheme = HarmonicScheme(m, alpha)
            F_matrix[i, j] = harmomic_scheme.harmony_score(X)
    (best_m_idx, best_alpha) = np.unravel_index( np.argmin(F_matrix), F_matrix.shape )
    best_m = template_types[best_m_idx]

    #best_m = "L"
    best_alpha = np.argmin(F_matrix[best_m_idx])
    #(best_m_idx, best_alpha) = np.unravel_index( np.argmin(F_matrix), F_matrix.shape )
    #best_m = template_types[best_m_idx]
    print(best_m)
    '''
    best_harmomic_scheme = HarmonicScheme('SET', colorType[Type]["alpha"])
    #heme = HarmonicScheme('T', 4)
    return best_harmomic_scheme

def BB(XT):
    F_matrix = np.zeros((M, A))
    for i in range(M):
        m = template_types[i]
        for j in range(A):
            print(i,j)
            alpha = 360/A * j
            harmomic_scheme = HarmonicScheme(m, alpha)

            for X in XT:
                F_matrix[i, j] += harmomic_scheme.harmony_score(X)

    (best_m_idx, best_alpha) = np.unravel_index( np.argmin(F_matrix), F_matrix.shape )
    best_m = template_types[best_m_idx]

    #best_m = "L"
    best_alpha = np.argmin(F_matrix[best_m_idx])
    #(best_m_idx, best_alpha) = np.unravel_index( np.argmin(F_matrix), F_matrix.shape )
    #best_m = template_types[best_m_idx]

    best_harmomic_scheme = HarmonicScheme(best_m, best_alpha)
    return best_harmomic_scheme
folder = 'pdf_img'
filelist = os.listdir(folder)
for filename in filelist:
    image_filename = folder+'/'+filename
# change image to width*height shape RGB tensor
color_image = cv2.imread(image_filename, cv2.IMREAD_COLOR)
weight,height = color_image.shape[0],color_image.shape[1]
color_image = cv2.resize(color_image, (int(color_image.shape[1]/2),int(color_image.shape[0]/2)),  interpolation=cv2.INTER_AREA)
print(color_image.shape)
#cv2.imshow("windows",color_image)
HSV_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
del color_image
gc.collect()
#cv2.imshow("windows",HSV_image)

best_harmomic_scheme = B(HSV_image)
print("Harmonic Scheme Type  : ", best_harmomic_scheme.m)
print("Harmonic Scheme Alpha : ", best_harmomic_scheme.alpha)

histo = util.count_hue_histogram(HSV_image)
canvas = util.draw_polar_histogram(histo)
overlay = util.draw_harmonic_scheme(best_harmomic_scheme, canvas)
#cv2.imshow("windows",overlay)
cv2.addWeighted(overlay, 0.5, canvas, 1 - 0.5, 0, canvas)
cv2.imwrite("hue_source.jpg", canvas)

del overlay
gc.collect()

num_superpixels = -1
new_HSV_image = best_harmomic_scheme.hue_shifted(HSV_image, num_superpixels)
#cv2.imshow("window",new_HSV_image)
'''
histo = util.count_hue_histogram(new_HSV_image)
canvas = util.draw_polar_histogram(histo)
overlay = util.draw_harmonic_scheme(best_harmomic_scheme, canvas)
cv2.addWeighted(overlay, 0.5, canvas, 1 - 0.5, 0, canvas)
cv2.imwrite("hue_target.jpg", canvas)
'''

result_image = cv2.cvtColor(new_HSV_image, cv2.COLOR_HSV2BGR)
color_image = cv2.resize(result_image, (height,weight), interpolation=cv2.INTER_AREA)
result_image = result_image.astype('int')
#cv2.imshow("windows",result_image)
cv2.imwrite("pdf_img/"+Type+".jpg", result_image)    

