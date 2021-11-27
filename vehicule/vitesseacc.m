%% Trajectoire

clear
clc
close all

% Vitesse

%Pourcentage	Vitesse (m/s)	Vitesse (m/s) selon courbe
%0	0	-0,012666667
%30	0,063	0,931333333
%40	0,089	1,246
%50	0,117	1,560666667
%60	0,147	1,875333333
%70	0,174	2,19
%80	0,208	2,504666667
%90	0,234	2,819333333
%100	0,27	3,134


x = [0 30 40 50 60 70 80 90 100];
y = [0 0.063 0.089 0.117 0.147 0.174 0.208 0.234 0.27];

pourcentage = 0:1:100;

N = length(x);

% Pour ce cas là, une ligne droite est la bonne chose à faire
% Donc 2 phis seulement

phi_1 = 1;
phi_2 = x;

P = [phi_1, phi_2(1);
     phi_1, phi_2(2);
     phi_1, phi_2(3);
     phi_1, phi_2(4);
     phi_1, phi_2(5);
     phi_1, phi_2(6);
     phi_1, phi_2(7);
     phi_1, phi_2(8);
     phi_1, phi_2(9);
];

Y = [y(1); y(2); y(3); y(4); y(5); y(6); y(7); y(8); y(9);];

A = pinv(P)*Y

y0 = A(1) + A(2)*pourcentage;

figure;
hold on;
plot(pourcentage,y0);
scatter(x, y,'filled');
hold off;

title('Vitesse du véhicule');
xlabel('Pourcentage commandé (%)');
ylabel('Vitesse (m/s))');
legend('Courbe approximée','Points existants');

% Accélération
%Pourcentage	Accélération (m/s2)	Vitesse (m/s)
%30	0,626	0,063
%40	0,9142	0,089
%50	1,371	0,117
%60	2,618	0,147
%70	4,11	0,174
%80	3,97	0,208
%90	4,608	0,234
%100	4,11	0,27

x = [0.063 0.089 0.117 0.147 0.174 0.234 0.27];
y = [0.626 0.9142 1.371 2.618 4.11 4.608 4.11];

vitesse = 0.063:0.0001:0.27

phi_1 = 1;
phi_2 = x;
phi_3 = x.^2;
phi_4 = x.^3;

P = [phi_1, phi_2(1), phi_3(1), phi_4(1);
     phi_1, phi_2(2), phi_3(2), phi_4(2);
     phi_1, phi_2(3), phi_3(3), phi_4(3);
     phi_1, phi_2(4), phi_3(4), phi_4(4);
     phi_1, phi_2(5), phi_3(5), phi_4(5);
     phi_1, phi_2(5), phi_3(6), phi_4(6);
     phi_1, phi_2(5), phi_3(7), phi_4(7);
];

Y = [y(1); y(2); y(3); y(4); y(5);y(6);y(7);];

A = pinv(P)*Y

y0 = A(1) + A(2)*vitesse + A(3)*vitesse.^2+ A(4)*vitesse.^3;
test = A(1) + A(2)*0.27 + A(3)*0.27^2+ A(4)*0.27^3;

figure;
hold on;
plot(vitesse,y0);
scatter(x, y,'filled');
hold off;

title('Accélération du véhicule');
xlabel('Différentiel de vitesse (m/s)');
ylabel('Accélération (m/s²)');
legend('Courbe approximée','Points existants');
