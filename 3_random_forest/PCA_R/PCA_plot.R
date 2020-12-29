# https://cran.r-project.org/web/packages/ggfortify/vignettes/plot_pca.html

autoplot(card_PCA, data = df, colour = 'Warrior')

autoplot(card_PCA, data = df, colour = 'Warlock')

autoplot(card_PCA, data = df, colour = 'Shaman')

autoplot(card_PCA, data = df, colour = 'game_count_RE')

autoplot(card_PCA, data = df, colour = 'win_rate_RE')

autoplot(card_PCA, data = df, colour = 'time_duration_RE')
