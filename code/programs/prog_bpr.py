#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:       Qiang Cui:  <cuiqiang1990[at]hotmail.com>
# Descripton:   纯RNN、GRU程序
# Create Date:  2017-05-19 12:00:00
# Modify Date:  2010-00-00 00:00:00
# Modify Disp:

from __future__ import print_function
from collections import OrderedDict     # 按输入的顺序构建字典
import time
import datetime
import numpy as np
import os
import random
from public.BPR import OboBpr, Bpr
from public.Global_Best import GlobalBest
from public.Valuate import fun_predict_auc_recall_map_ndcg
from public.Valuate import fun_save_best_and_losses
from public.Load_Data_by_length import load_data, fun_data_buys_masks
from public.Load_Data_by_length import fun_random_neg_masks_tra, fun_random_neg_masks_tes
__docformat__ = 'restructedtext en'

WHOLE = 'E:/Projects/datasets/'
# WHOLE = '/home/cuiqiang/2_Datasets/'
# WHOLE = '/home/wushu/usr_cuiqiang/2_Datasets/'
# WHOLE = '/mnt/dev_sdb1/cuiqiang/2_Datasets/'
PATH_t30 = os.path.join(WHOLE, 'taobao_users_30_100/')
PATH_t55 = os.path.join(WHOLE, 'taobao_users_5_100_5000hang/')
PATH_o10 = os.path.join(WHOLE, 'outbrain_users_10_100/')
PATH = PATH_t55


def exe_time(func):
    def new_func(*args, **args2):
        name = func.__name__
        start = datetime.datetime.now()
        print("-- {%s} start: @ %ss" % (name, start))
        back = func(*args, **args2)
        end = datetime.datetime.now()
        print("-- {%s} start: @ %ss" % (name, start))
        print("-- {%s} end:   @ %ss" % (name, end))
        total = (end - start).total_seconds()
        print("-- {%s} total: @ %.3fs = %.3fh" % (name, total, total / 3600.0))
        return back
    return new_func


class Params(object):
    def __init__(self, p=None):
        """
        构建模型参数，加载数据
            把前90%分为8:1用作train和valid，来选择超参数, 不用去管剩下的10%.
            把前90%作为train，剩下的是test，把valid时学到的参数拿过来跑程序.
            valid和test部分，程序是一样的，区别在于送入的数据而已。
        :param p: 一个标示符，没啥用
        :return:
        """
        # 1. 建立各参数。要调整的地方都在 p 这了，其它函数都给写死。
        if not p:
            t = 't'                       # 写1就是valid, 写0就是test
            assert 't' == t or 'v' == t   # no other case
            p = OrderedDict(
                [
                    ('dataset',             'user_buys.txt'),
                    ('mode',                'test' if 't' == t else 'valid'),
                    ('split',               [0.8, 1.0] if 't' == t else [0.6, 0.8]),   # no third case
                    ('at_nums',             [5, 10, 15, 20]),
                    ('epochs',              100),

                    ('latent_size',         20),
                    ('alpha',               0.01),
                    ('lambda',              0.01),

                    ('mini_batch',          0),     # 0:one_by_one, 1:mini_batch
                    ('bpr',                 0),     # 0:bpr

                    ('batch_size_train',    1),     # 4比较合适。
                    ('batch_size_test',     768),   # user * item 矩阵太大了，分成多次计算。 768
                ])
            for i in p.items():
                print(i)

        # 2. 加载数据
        # 因为train/set里每项的长度不等，无法转换为完全的(n, m)矩阵样式，所以shared会报错.
        global PATH
        [(user_num, item_num), (tra_buys, tes_buys)] = \
            load_data(os.path.join(PATH, p['dataset']), p['mode'], p['split'])
        # 正样本加masks
        tra_buys_masks, tra_masks = fun_data_buys_masks(tra_buys, tail=[item_num])          # 预测时算用户表达用
        tes_buys_masks, tes_masks = fun_data_buys_masks(tes_buys, tail=[item_num])          # 预测时用
        # 负样本加masks
        tra_buys_neg_masks = fun_random_neg_masks_tra(item_num, tra_buys_masks)   # 训练时用（逐条、mini-batch均可）
        tes_buys_neg_masks = fun_random_neg_masks_tes(item_num, tra_buys_masks, tes_buys_masks)   # 预测时用

        # 3. 创建类变量
        self.p = p
        self.user_num, self.item_num = user_num, item_num
        self.tra_buys_masks, self.tra_masks, self.tra_buys_neg_masks = tra_buys_masks, tra_masks, tra_buys_neg_masks
        self.tes_buys_masks, self.tes_masks, self.tes_buys_neg_masks = tes_buys_masks, tes_masks, tes_buys_neg_masks

    def build_model_one_by_one(self, flag):
        """
        建立模型对象
        :param flag: 参数变量、数据
        :return:
        """
        print('Building the model one_by_one ...')      # mask只是test计算用户表达时用。
        assert flag in [0]
        p = self.p
        size = p['latent_size']
        model = OboBpr(
            train=[self.tra_buys_masks, self.tra_masks, self.tra_buys_neg_masks],
            test =[self.tes_buys_masks, self.tes_masks, self.tes_buys_neg_masks],
            alpha_lambda=[p['alpha'], p['lambda']],
            n_user=self.user_num,
            n_item=self.item_num,
            n_in=size,
            n_hidden=size)
        model_name = model.__class__.__name__
        print('\t the current Class name is: {val}'.format(val=model_name))
        return model, model_name, size

    def build_model_mini_batch(self, flag):
        """
        建立模型对象
        :param flag: 参数变量、数据
        :return:
        """
        print('Building the model mini_batch ...')      # mask只是test计算用户表达时用。
        assert flag in [0]
        p = self.p
        size = p['latent_size']
        model = Bpr(
            train=[self.tra_buys_masks, self.tra_masks, self.tra_buys_neg_masks],
            test =[self.tes_buys_masks, self.tes_masks, self.tes_buys_neg_masks],
            alpha_lambda=[p['alpha'], p['lambda']],
            n_user=self.user_num,
            n_item=self.item_num,
            n_in=size,
            n_hidden=size)
        model_name = model.__class__.__name__
        print('\t the current Class name is: {val}'.format(val=model_name))
        return model, model_name, size

    def compute_start_end(self, flag):
        """
        获取mini-batch的各个start_end(np.array类型，一组连续的数值)
        :param flag: 'train', 'test'
        :return: 各个start_end组成的list
        """
        assert flag in ['train', 'test', 'test_auc']
        if 'train' == flag:
            size = self.p['batch_size_train']
        elif 'test' == flag:
            size = self.p['batch_size_test']        # test: top-k and acquire user vector
        else:
            size = self.p['batch_size_test'] * 10   # test: auc
        user_num = self.user_num
        rest = (user_num % size) > 0   # 能整除：rest=0。不能整除：rest=1，则多出来一个小的batch
        n_batches = np.minimum(user_num // size + rest, user_num)
        batch_idxs = np.arange(n_batches, dtype=np.int32)
        starts_ends = []
        for bidx in batch_idxs:
            start = bidx * size
            end = np.minimum(start + size, user_num)   # 限制标号索引不能超过user_num
            start_end = np.asarray(np.arange(start, end, dtype=np.int32))
            starts_ends.append(start_end)
        return batch_idxs, starts_ends


def train_valid_or_test():
    """
    主程序
    :return:
    """
    # 建立参数、数据、模型、模型最佳值
    pas = Params()
    p = pas.p
    if 0 == p['mini_batch']:
        model, model_name, size = pas.build_model_one_by_one(flag=p['bpr'])
    else:
        model, model_name, size = pas.build_model_mini_batch(flag=p['bpr'])
    best = GlobalBest(at_nums=p['at_nums'])   # 存放最优数据
    batch_idxs_tra, starts_ends_tra = pas.compute_start_end(flag='train')
    _, starts_ends_tes = pas.compute_start_end(flag='test')
    _, starts_ends_auc = pas.compute_start_end(flag='test_auc')

    # 直接取出来部分变量，后边就不用加'pas.'了。
    user_num, item_num = pas.user_num, pas.item_num
    tra_buys_masks, tra_masks, tra_buys_neg_masks = pas.tra_buys_masks, pas.tra_masks, pas.tra_buys_neg_masks
    tes_buys_masks, tes_masks, tes_buys_neg_masks = pas.tes_buys_masks, pas.tes_masks, pas.tes_buys_neg_masks
    del pas

    # 主循环
    losses = []
    times0, times1, times2, times3 = [], [], [], []
    for epoch in np.arange(p['epochs']):
        print("Epoch {val} ==================================".format(val=epoch))
        # 每次epoch，都要重新选择负样本。都要把数据打乱重排，这样会以随机方式选择样本计算梯度，可得到精确结果
        if epoch > 0:       # epoch=0的负样本已在循环前生成，且已用于类的初始化
            tra_buys_neg_masks = fun_random_neg_masks_tra(item_num, tra_buys_masks)
            tes_buys_neg_masks = fun_random_neg_masks_tes(item_num, tra_buys_masks, tes_buys_masks)
            model.update_neg_masks(tra_buys_neg_masks, tes_buys_neg_masks)

        # ----------------------------------------------------------------------------------------------------------
        print("\tTraining ...")
        t0 = time.time()
        loss = 0.
        random.seed(str(123 + epoch))
        if 0 == p['mini_batch']:
            user_idxs_tra = np.arange(user_num, dtype=np.int32)
            random.shuffle(user_idxs_tra)       # 每个epoch都打乱user_id输入顺序
            for uidx in user_idxs_tra:
                tra = tra_buys_masks[uidx]
                neg = tra_buys_neg_masks[uidx]
                for i in np.arange(sum(tra_masks[uidx])):
                    loss += model.train(uidx, [tra[i], neg[i]])
        else:
            random.shuffle(batch_idxs_tra)      # 每个epoch都打乱batch_idx输入顺序
            for bidx in batch_idxs_tra:
                start_end = starts_ends_tra[bidx]
                random.shuffle(start_end)       # 打乱batch内的indexes
                usrs = start_end
                tras = tra_buys_masks[start_end]        # 每个用户的正样本序列是一行。共多行。
                negs = tra_buys_neg_masks[start_end]
                msks = tra_masks[start_end]
                for j in np.arange(max(np.sum(msks, axis=1))):
                    loss += model.train(usrs, [tras[:, j], negs[:, j]], msks[:, j])   # 每次取某一列(各usr的第j个item)
        rnn_l2_sqr = model.l2.eval()            # model.l2是'TensorVariable'，无法直接显示其值
        print('\t\tsum_loss = {val} = {v1} + {v2}'.format(val=loss + rnn_l2_sqr, v1=loss, v2=rnn_l2_sqr))
        losses.append('{v1}'.format(v1=int(loss + rnn_l2_sqr)))
        t1 = time.time()
        times0.append(t1 - t0)

        # ----------------------------------------------------------------------------------------------------------
        print("\tPredicting ...")
        # 计算：所有用户、商品的表达
        model.update_trained_items()    # 对于MV-GRU，这里会先算出来图文融合特征。
        model.update_trained_users()
        t2 = time.time()
        times1.append(t2 - t1)

        # 计算各种指标，并输出当前最优值。
        fun_predict_auc_recall_map_ndcg(
            p, model, best, epoch, starts_ends_auc, starts_ends_tes, tes_buys_masks, tes_masks)
        best.fun_print_best(epoch)   # 每次都只输出当前最优的结果
        t3 = time.time()
        times2.append(t3-t2)
        print('\tavg. time (train, user, test): %0.0fs,' % np.average(times0),
              '%0.0fs,' % np.average(times1), '%0.0fs' % np.average(times2),
              '| alpha, lam: {v1}'.format(v1=', '.join([str(lam) for lam in [p['alpha'], p['lambda']]])),
              '| model: {v1}'.format(v1=model_name))

        # ----------------------------------------------------------------------------------------------------------
        if epoch == p['epochs'] - 1:
            # 保存最优值、所有的损失值。
            print("\tBest and losses saving ...")
            path = os.path.join(os.path.split(__file__)[0], '..', 'Results_best_and_losses', PATH.split('/')[-2])
            fun_save_best_and_losses(path, model_name, epoch, p, best, losses)

    for i in p.items():
        print(i)
    print('\t the current Class name is: {val}'.format(val=model_name))


@exe_time
def main():
    train_valid_or_test()


if '__main__' == __name__:
    main()
