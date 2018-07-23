library(tidyverse)
library(lme4)
rm(list = ls())

lf <- function(f) {
  d <- read.csv(f, sep = '\t')
  d$unig <- -log(d$FREQUENCY / sum(d$FREQUENCY)) / log(2)
  d
}

model_arch <- function(d) {
  m <- lm(data = subset(d, MONOMORPHEME == T), SEQ_INFO ~ POSITION + unig)
}


eng <- lf('~/Desktop/seginfo/newdict/eng.txt')
# r2 for the model with REAL english data
real_r2 = summary(model_arch(eng))$r.squared
# 3rd factor(1 = intercept, 2 = position, 3 = unigram info), 3rd attribute (1 = estimate, 2 = se, 3 = t-value)
real_t <- summary(model_arch(eng))$coefficient[3,3]

lexicons <- data.frame(r2 = real_r2, t = real_t, cond =  'Original')

# go through all seg info data files for scrambled lexicons
scr_r2 <- c()
for (f in list.files('~/Desktop/seginfo/newdict/randos/')) {
  # for the impatient among us (i.e. me), print out the name of the file
  print(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # load in the scrambled lexicon segment info data
  scr <- lf(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # fit the model
  mod <- lm(data = subset(scr, MONOMORPHEME == T), SEQ_INFO ~ POSITION + unig)
  mod_summary <- summary(mod)
  # save the r2 and t-value for the effect of unig info 
  lex <- data.frame(r2 = mod_summary$r.squared, t = mod_summary$coefficient[3,3], cond =  'Scrambled')
  lexicons <- rbind(lexicons, lex)
}

write.csv('~/Desktop/seginfo/r_code/scrambled_lex.csv', quote = F, row.names = F)

# pretty plots
# no stats on the results b/c, well, don't really need it :)
# r2
ggplot(data = lexicons, aes(r2, group = cond, fill = cond)) + 
  geom_histogram(position="stack",alpha=0.5,binwidth=0.0025) +
  xlab('R2') + ylab('Count') +
  scale_fill_discrete(name="Lexicon Type", labels = c('Original', 'Scrambled Frequencies')) +
  geom_segment(aes(x = real_r2, y = 45, xend = real_r2, yend = 10),
               arrow = arrow(length = unit(0.5, "cm")))

# t-value
ggplot(data = lexicons, aes(t, group = cond, fill = cond)) + 
  geom_histogram(position="stack") +
  xlab('t-value') + ylab('Count') +
  scale_fill_discrete(name="Lexicon Type", labels = c('Original', 'Scrambled Frequencies')) +
  geom_segment(aes(x = real_t, y = 45, xend = real_t, yend = 10),
               arrow = arrow(length = unit(0.5, "cm")))
