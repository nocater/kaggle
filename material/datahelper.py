import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split


class feature_energing:
    """
        数据处理
        使用：
            fe = feature_energing=(file, params)
            fe.preprocess()
        属性
        origin_df:原始CSV数据
        target_df:处理后数据(需要执行preprocess)
        origin_range:原始数据范围
        target_range：处理后数据范围
        X:自变量df
        Y:因变量df
    """

    def __init__(self, file,
                 columns: '选取的数据维度' = ['C', 'Si', 'Mn', 'Ni', 'Cr', 'Mo', 'Al', 'Co', '等温温度T2', '回火温度T3', '抗拉强度'],
                 scaler: '是否采用数据缩放' = StandardScaler,
                 regression: '用于分类还是回归' = True,
                 shuffle: '' = True,
                 random_seed: '' = 1,
                 categories: '分类类别' = 4,
                 onehot: '是否使用onehot' = False,
                 info: '是否打印信息' = True,
                 ranges: '数据范围' = {'C': [0, 1.2],
                                   'Si': [0, 4],
                                   'T2': [1, 720],
                                   'T3': [25, 450],
                                   'Y': [900, 2500],
                                   },
                 dic_rename: '列名更改' = {'等温温度T2': 'T2', '回火温度T3': 'T3', '抗拉强度': 'Y'},
                 Ys=1,
                 ):
        self.columns = columns
        self.scaler = scaler
        self.regression = regression
        self.shuffle = shuffle
        self.random_seed = random_seed
        self.categories = categories
        self.onehot = onehot
        self.info = info
        self.ranges = ranges
        self.origin_df = pd.read_excel(file, header=2)
        self.origin_df = self.origin_df[self.origin_df.index.notnull()]
        self.dic_rename = dic_rename
        self.Ys = Ys

    def preprocess(self):
        """
        对数据进行处理
        :return:
        """
        if self.info: print('对数据进行回归处理' if self.regression else '对数据进行分类处理')

        df = self.origin_df[self.columns]
        if self.info:
            print('列名:', df.columns)
            df.info()

        # 重命名列名
        df = df.rename(columns=self.dic_rename)

        ## 数据处理
        df = df.fillna(value=0)

        # 转成Float
        df = df.loc[:, :].apply(pd.to_numeric, errors='coerce')

        # 强度处理
        df = df[df.Y >= self.ranges['Y'][0]]
        df = df[df.Y <= self.ranges['Y'][1]]
        if self.info: print('--Del Y not in range:', np.shape(df))

        # C处理 Nan的为不是数字的
        df = df[df.C.notnull()]
        df = df[df.C >= self.ranges['C'][0]]
        df = df[df.C <= self.ranges['C'][1]]
        if self.info: print('--Del C not in range:', np.shape(df))

        #
        # T2
        df = df[df.T2.notnull()]
        if 'T2' in self.ranges.keys():
            df = df[df.T2 >= self.ranges['T2'][0]]
            df = df[df.T2 <= self.ranges['T2'][1]]
        if self.info:print('--Del T2 None', np.shape(df))

        #
        df.loc[(df.T3 == 0), 'T3'] = 25
        df = df[df.T3 >= self.ranges['T3'][0]]
        df = df[df.T3 <= self.ranges['T3'][1]]
        if self.info: print('--Del T3 not in range:', np.shape(df))

        # 其它元素位置 None填充0
        df = df.fillna(value=0)
        ##

        # 各维度最大最小值
        mins = np.min(df, axis=0)
        maxs = np.max(df, axis=0)
        self.origin_range = pd.DataFrame([mins, maxs], index=['min:', 'max'], columns=self.columns)
        # if self.info: print('原始数据范围:', self.origin_range, sep='\n')

        X = df.iloc[:, :-self.Ys].values
        y = df.Y.values
        if not self.regression:  # 非回归处理label
            y = self.deal_labels(y)

        self.target_df = df

        self.X = X
        self.Y = y
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=self.shuffle,
                                                            random_state=self.random_seed)

        # 数据缩放
        if self.regression:
            s = MinMaxScaler().fit(X_train)
            X_train = s.transform(X_train)
            X_test = s.transform(X_test)

            y_train = (y_train - 900) / (2500 - 900)
            y_test = (y_test - 900) / (2500 - 900)

        # 各维度最大最小值
        mins = np.min(df, axis=0)
        maxs = np.max(df, axis=0)
        self.target_range = pd.DataFrame([mins, maxs], index=['min:', 'max'], columns=df.columns)
        if self.info: print('处理后各维度范围:', self.target_range, sep='\n')

        self.X_train = X_train
        self.y_trian = y_train
        self.X_test = X_test
        self.y_test = y_test
        print('处理完成:', np.shape(df))
        return X_train, X_test, y_train, y_test

    def deal_labels(self, y):
        """
        将类别进行离散表示
        """
        min_ = np.min(y)
        max_ = np.max(y)

        # 设置分类边界
        bounds = np.linspace(min_ - 1, max_, self.categories + 1)

        if self.info: print('类别统计:', np.histogram(y, bounds)[0])

        # 画图
        if False:
            from matplotlib import pyplot as plt
            plt.hist(y, bounds)
            plt.title('Split Data with 4 categories')
            plt.xlabel('Tensile Strength')
            plt.ylabel('Count')
            plt.show()

        # 转换类别编号
        y = [(bounds >= i).nonzero()[0][0] for i in y]
        # 编号下标从0开始
        y = y - np.array([1])
        y = y.ravel()

        # 是否使用onehot表示类别
        if self.onehot:
            y = np.array(y).reshape(-1, 1)
            enc = OneHotEncoder()
            y = enc.fit_transform(y).toarray()
        return y


def compute_pearson(x, y):
    """
    计算pearson系数
    :param x:
    :param y:
    :return:
    """
    pearson = []
    for i in range(x.shape[1]):
        x_ = np.hstack(x[:, i])
        y_ = np.hstack(y)
        pearson.append(np.corrcoef(x_, y_)[1, 0])
    return pearson
    pass


def drawpic(df):
    from matplotlib import pyplot as plt
    plt.scatter(df.C, df.Y)
    plt.title('Carbon and tensile strength relationship scatter plot')
    plt.xlabel('Carbon content (wt.%)')
    plt.ylabel('Tensile Strength (MPa)')
    plt.show()


def evaluate_classifier(y, y_pred):
    """
    评估
    :param y:
    :param y_predt:
    :return:
    """
    # 计算F1 Recall support
    from sklearn.metrics import precision_recall_fscore_support as score
    precision, recall, fscore, support = score(y, y_pred)
    table = pd.DataFrame({'precision': precision, 'recall': recall, 'fscore': fscore, 'support': support})
    print(table)
    return table


def evaluate_regression(y, y_pred):
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    y = y.ravel()
    y_pred = y_pred.ravel()
    print(f'MAE:{int(mean_absolute_error(y, y_pred))}')
    print(f'MSE:{int(mean_squared_error(y, y_pred))}')
    print(f'RMSE:{int(np.sqrt(mean_squared_error(y, y_pred)))}')
    print('抽样随机结果对比：')
    index = np.random.randint(1, 100)
    result = pd.DataFrame([y[index:index + 5], y_pred[index:index + 5]], index=['y', 'y_pred'])
    # print(result)
    pass