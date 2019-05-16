
% gru, t3, 0.01/100, hca_gru, split=0.8
x1 = 1:1:50;
y1 = [1534205, 1107812, 981482, 920229, 878170, 842361, 810395, 778322, 748667, 720257, 694629, 668998, 645523, 623281, 602942, 582771, 565414, 548812, 533223, 518028, 505540, 493680, 481808, 476246, 464198, 450749, 443360, 433624, 426371, 422487, 412768, 404793, 397566, 392600, 385514, 382161, 375761, 370497, 366026, 361340, 357823, 352883, 356397, 347414, 340699, 337604, 334045, 330645, 329517, 325628];

% gru, t3, 0.05/50, mv_gru, split=0.9
x2 = 1:1:50;
y2 = [1446450, 1022308, 894951, 830431, 785097, 746192, 712407, 678042, 646251, 615282, 588684, 561423, 536788, 513773, 492132, 471742, 453795, 436666, 421585, 406764, 394352, 381940, 370100, 359959, 348506, 339135, 331558, 322713, 315070, 307214, 301287, 295406, 288118, 282403, 276591, 271640, 267099, 261875, 257530, 254014, 249397, 246077, 242285, 238895, 234643, 230965, 228476, 225054, 223467, 220438];

figure();
plot(x1, y1, 'LineWidth', 1);
hold on;
plot(x2, y2, 'LineWidth', 1);
% ylim([0, 900000]);
title('loss curve')

alphas = {'alpha=0.1, gru', 'alpha=0.1, hca x3'};
leg = legend(alphas);
set(leg)









