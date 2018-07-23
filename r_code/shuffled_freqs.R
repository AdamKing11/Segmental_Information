library(tidyverse)
library(lme4)
rm(list = ls())

lf <- function(f) {
  d <- read.csv(f, sep = '\t')
  d$unig <- -log(d$FREQUENCY / sum(d$FREQUENCY)) / log(2)
  d
}

model_arch <- function(d) {
  m <- lmer(data = subset(d, MONOMORPHEME == T), SEQ_INFO ~ POSITION + unig + (1|WORD))
}


eng <- lf('~/Desktop/seginfo/newdict/eng.txt')
# 3rd factor(1 = intercept, 2 = position, 3 = unigram info), 3rd attribute (1 = estimate, 2 = se, 3 = t-value)
real_t <- summary(model_arch(eng))$coefficient[3,3]

lexicons <- data.frame(t = real_t, cond =  'Original')

# go through all seg info data files for scrambled lexicons
for (f in list.files('~/Desktop/seginfo/newdict/randos/')) {
  # for the impatient among us (i.e. me), print out the name of the file
  print(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # load in the scrambled lexicon segment info data
  scr <- lf(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # fit the model
  mod <- model_arch(scr)
  mod_summary <- summary(mod)
  # save the t-value for the effect of unig info 
  lex <- data.frame(t = mod_summary$coefficient[3,3], cond =  'Scrambled')
  lexicons <- rbind(lexicons, lex)
}

write.csv(lexicons, '~/Desktop/seginfo/r_code/scrambled_lex.csv', quote = F, row.names = F)

# probability of a shuffled lexicon has a t-value less than the real one:
print(sum(lexicons$t < real_t)) / (nrow(lexicons) - 1)


# pretty plot
# t-value
ggplot(data = lexicons, aes(t, group = cond, fill = cond)) + 
  geom_histogram(position="stack") +
  xlab('t-value') + ylab('Count') +
  scale_fill_discrete(name="Lexicon Type", labels = c('Original', 'Scrambled Frequencies')) +
  geom_segment(aes(x = real_t, y = 45, xend = real_t, yend = 10),
               arrow = arrow(length = unit(0.5, "cm")))
