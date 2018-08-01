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
  m
}

model_arch_2 <- function(d) {
  m <- lmer(data = subset(d, MONOMORPHEME == T), SEQ_INFO ~ POSITION * unig + (1|WORD))
  m
}


eng <- lf('~/Desktop/seginfo/newdict/eng.txt')
rev <- lf('~/Desktop/seginfo/newdict/rev-eng.txt')



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
ggsave('~/Desktop/seginfo/r_code/t_vals.png')


### for interaction
real_t <- summary(model_arch_2(eng))$coefficient[4,3]
lexicons <- data.frame(t = real_t, cond =  'Original')
# go through all seg info data files for scrambled lexicons
for (f in list.files('~/Desktop/seginfo/newdict/randos/')) {
  # for the impatient among us (i.e. me), print out the name of the file
  print(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # load in the scrambled lexicon segment info data
  scr <- lf(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # fit the model
  mod <- model_arch_2(scr)
  mod_summary <- summary(mod)
  # save the t-value for the effect of unig info 
  lex <- data.frame(t = mod_summary$coefficient[4,3], cond =  'Scrambled')
  lexicons <- rbind(lexicons, lex)
}
ggplot(data = lexicons, aes(t, group = cond, fill = cond)) + 
  geom_histogram(position="stack") +
  xlab('t-value') + ylab('Count') +
  scale_fill_discrete(name="Lexicon Type", labels = c('Original', 'Scrambled Frequencies')) +
  geom_segment(aes(x = real_t, y = 45, xend = real_t, yend = 10),
               arrow = arrow(length = unit(0.5, "cm")))


# some other stuff
model_arch_3 <- function(d) {
  d <- subset(d, LENGTH < 10)
  lmer(data = subset(d, SEQ_INFO > 0), SEQ_INFO ~ as.factor(POSITION):unig + (1|LENGTH) + (1|WORD)) 
}

get_ts <- function(d, lex.cond = 'shuffled') {
  m <- model_arch_3(d)
  df <- data.frame(pos = integer(), t.val = double(), lex.cond = character())
  sm <- summary(m)
  for (i in 2:10) {
    df <- rbind(df, data.frame(pos = i-1, t.val = sm$coefficient[i,3], lex.cond = lex.cond))
  }
  df
}

all_ts <- get_ts(eng, 'original')

for (f in list.files('~/Desktop/seginfo/newdict/randos/')) {
  # for the impatient among us (i.e. me), print out the name of the file
  print(paste0('~/Desktop/seginfo/newdict/randos/', f))
  # load in the scrambled lexicon segment info data
  scr <- lf(paste0('~/Desktop/seginfo/newdict/randos/', f))
  
  scr_ts <- get_ts(scr)
  all_ts <- rbind(all_ts, scr_ts)
}

all_ts <- read.csv('~/Desktop/seginfo/r_code/scrambled_lex.tvals.csv')
all_ts <- rbind(all_ts, get_ts(rev, 'reverse'))
write.csv(all_ts, '~/Desktop/seginfo/r_code/scrambled_lex.tvals.csv', quote = F, row.names = F)


og_ts <- subset(all_ts, lex.cond == 'original', select = -c(lex.cond))
names(og_ts)[2] <- 'og.tval'
all_ts <- left_join(all_ts, og_ts)
all_ts$t.val.proportion <- all_ts$t.val / all_ts$og.tval
all_ts$t.val.diff <- all_ts$og.tval - all_ts$t.val

ggplot(data = all_ts, aes(x = pos, y = t.val.proportion, color = lex.cond)) + geom_point(alpha = .2) + geom_line()
ggplot(data = all_ts, aes(x = pos, y = t.val.diff, color = lex.cond)) + geom_point(alpha = .2) + geom_line()
