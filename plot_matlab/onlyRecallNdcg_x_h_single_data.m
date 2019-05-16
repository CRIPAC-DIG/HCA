
% ==========================================================================
% ���������������ݼ��� LCA-GRU-x2345/h2345 ����ָ���ڲ�ͬtop-k�µı仯�����
% ���ݼ�: t3, o1
% ����: 'x2', 'x3', 'x4', 'x5', 
%       'h2', 'h3', 'h4', 'h5' 
% ָ��:  recall, map, ndcg
% ����:  top-k = 5, 10, 15, 20
clear;
clc;

data_dataset = {
    'TaoBao', 'Outbrain'};
data_method = {
    'x2', 'x3', 'x4', 'x5', ...
    'h2', 'h3', 'h4', 'h5'};
data_method_x = {'x2', 'x3', 'x4', 'x5'};
data_method_h = {'h2', 'h3', 'h4', 'h5'};
data_evaluation = {
    'Recall', 'NDCG', 'Recall', 'NDCG'};
data_top_k = [
    5, 10, 15];

% taobao���ݼ���3��ָ����8�ַ�����top-kֵ
t3_recall_x = {
    [0.6187, 0.9900, 1.3359]
    [0.7236, 1.1491, 1.4796]
    [0.7260, 1.1461, 1.4934]    % x4 top-20���
    [0.7337, 1.1618, 1.4960]};  % x5 top-5/10/15
t3_recall_h = {
    [0.7142, 1.1408, 1.4948]    % h2 top-20
    [0.7113, 1.0930, 1.4086]
    [0.7335, 1.1438, 1.4817]    % h4 top-15
    [0.7347, 1.1452, 1.4723]};  % h5 top-5/10
t3_ndcg_x = { 
    [1.2749, 1.3367, 1.4547]
    [1.5484, 1.6099, 1.7387]    % x3 �����
    [1.4543, 1.5194, 1.6555]
    [1.5119, 1.5705, 1.7031]};
t3_ndcg_h = {
    [1.5177, 1.5668, 1.7023]
    [1.5134, 1.5429, 1.6655]
    [1.5474, 1.5850, 1.7146]
    [1.5686, 1.6001, 1.7268]};  % h5�����
t3 = {
    t3_recall_x, t3_ndcg_x, ...
    t3_recall_h, t3_ndcg_h};

% outbrain���ݼ���3��ָ����8�ַ�����top-kֵ
o1_recall_x = {  
    [13.4848, 19.0333, 21.7444]
    [14.5518, 20.2134, 25.3466]
    [11.7452, 20.9472, 26.1368]    % x4 top-10/15/20
    [14.9729, 20.5433, 23.9854]};  % x5 top-5
o1_recall_h = {
    [11.2593, 18.6999, 22.0209]
    [14.5617, 19.9930, 24.0104]    % h3�����
    [11.9055, 19.1321, 23.0344]
    [13.6326, 19.6146, 23.0484]};
o1_ndcg_x = {    
    [13.2373, 15.5510, 16.4976]    % x2�����
    [12.1238, 14.8190, 16.2621]
    [ 9.4468, 12.2903, 14.7678]
    [12.7393, 15.0983, 16.4096]};
o1_ndcg_h = {
    [ 9.8284, 12.9713, 14.1256]
    [12.9881, 15.3525, 16.5222]    % h3�����
    [ 9.6851, 12.4649, 13.9295]
    [12.0613, 14.6472, 15.6654]};  
o1 = {
    o1_recall_x, o1_ndcg_x, ...
    o1_recall_h, o1_ndcg_h};

save onlyRecallNdcg_x_h_single_data
clear t3_recall_x t3_ndcg_x 
clear t3_recall_h t3_ndcg_h 
clear o1_recall_x o1_ndcg_x 
clear o1_recall_h o1_ndcg_h 

disp('Saving to: onlyRecallNdcg_x_h_single_data.mat');

