
library(influxdbr)
library(zoo)
library(xts)
library(cowplot)
library(reshape2)
library(scales)
library(hms)
library(ggplot2)
library(forcats)

# create connection to database
con <- influx_connection(host="192.168.0.94",user="lrdata",pass="Edge")
db <-"metrics_v2"
# queries for transactions and blocks
query_tx <- "select mean(*) from \"sawtooth_validator.chain.ChainController.committed_transactions_gauge\" where host = 'edg10' group by time(1s) fill(previous)"
query_bx <- "select mean(*) from \"sawtooth_validator.chain.ChainController.block_num\" where host = 'edg10' group by time(1s) fill(previous)"

# store query results
data_tx <- influx_query(con, db, query_tx, return_xts=FALSE)
data_bx <- influx_query(con, db, query_bx, return_xts=FALSE)

# query results to data frame
df_tx <- as.data.frame(data_tx)
df_bx <- as.data.frame(data_bx)

# prep tx data
df_tx_time_values <- as.data.frame(df_tx[,4:5])
df_tx_time_values$txns <- ave(df_tx_time_values$mean_value, FUN = function(x) c(0, diff(x)))
df_tx_time_values_xts <- as.xts(df_tx_time_values$txns, order.by=df_tx_time_values$time)

# slice tx data
tps_2 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-15 09:00:00",end="2022-04-15 09:59:59")))
tps_4 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-16 10:30:00",end="2022-04-16 11:29:59")))
tps_6 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-16 11:45:00",end="2022-04-16 12:44:59")))
tps_8 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-18 19:30:00",end="2022-04-18 20:29:59")))
tps_10 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-18 20:45:00",end="2022-04-18 21:44:59")))
tps_12 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-18 22:00:00",end="2022-04-18 22:59:59")))
tps_10_8 <- c(coredata(window(df_tx_time_values_xts,start="2022-05-01 12:15:00",end="2022-05-01 13:14:59")))
tps_10_10 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-19 19:30:00",end="2022-04-19 20:29:59")))
tps_10_12 <- c(coredata(window(df_tx_time_values_xts,start="2022-05-01 13:30:00",end="2022-05-01 14:29:59")))
tps_10_20 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-19 20:45:00",end="2022-04-19 21:44:59")))

# present tx data
df_tx_results <- data.frame(tps_2,tps_4,tps_6,tps_8,tps_10,tps_12,tps_10_8,tps_10_10,tps_10_12,tps_10_20)
summary(df_tx_results)

# prep bx data
df_bx_time_values <- as.data.frame(df_bx[,4:5])
df_bx_time_values$txns <- ave(df_bx_time_values$mean_value, FUN = function(x) c(0, diff(x)))
df_bx_time_values_xts <- as.xts(df_bx_time_values$txns, order.by=df_bx_time_values$time)

# slice bx data
bps_2 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-15 09:00:00",end="2022-04-15 09:59:59")))
bps_4 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-16 10:30:00",end="2022-04-16 11:29:59")))
bps_6 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-16 11:45:00",end="2022-04-16 12:44:59")))
bps_8 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-18 19:30:00",end="2022-04-18 20:29:59")))
bps_10 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-18 20:45:00",end="2022-04-18 21:44:59")))
bps_12 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-18 22:00:00",end="2022-04-18 22:59:59")))
bps_10_8 <- c(coredata(window(df_bx_time_values_xts,start="2022-05-01 12:15:00",end="2022-05-01 13:14:59")))
bps_10_10 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-19 19:30:00",end="2022-04-19 20:29:59")))
bps_10_12 <- c(coredata(window(df_bx_time_values_xts,start="2022-05-01 13:30:00",end="2022-05-01 14:29:59")))
bps_10_20 <- c(coredata(window(df_bx_time_values_xts,start="2022-04-19 20:45:00",end="2022-04-19 21:44:59")))

# present bx data
df_bx_results <- data.frame(bps_2,bps_4,bps_6,bps_8,bps_10,bps_12,bps_10_8,bps_10_10,bps_10_12,bps_10_20)
summary(df_bx_results)

# present tx and bx data together
df_bx_tx_results <- data.frame(bps_2,tps_2,bps_4,tps_4,bps_6,tps_6,bps_8,tps_8,bps_10,tps_10,bps_12,tps_12,bps_10_8,tps_10_8,bps_10_10,tps_10_10,bps_10_12,tps_10_12,bps_10_20,tps_10_20)
summary(df_bx_tx_results)

# mean transactions per block
avg_bx_tps_2 <- sum(df_bx_tx_results$tps_2) / sum(df_bx_tx_results$bps_2) 
avg_bx_tps_4 <- sum(df_bx_tx_results$tps_4) / sum(df_bx_tx_results$bps_4) 
avg_bx_tps_6 <- sum(df_bx_tx_results$tps_6) / sum(df_bx_tx_results$bps_6) 
avg_bx_tps_8 <- sum(df_bx_tx_results$tps_8) / sum(df_bx_tx_results$bps_8) 
avg_bx_tps_10 <- sum(df_bx_tx_results$tps_10) / sum(df_bx_tx_results$bps_10) 
avg_bx_tps_12 <- sum(df_bx_tx_results$tps_12) / sum(df_bx_tx_results$bps_12) 
avg_bx_tps_10_8 <- sum(df_bx_tx_results$tps_10_8) / sum(df_bx_tx_results$bps_10_8) 
avg_bx_tps_10_10 <- sum(df_bx_tx_results$tps_10_10) / sum(df_bx_tx_results$bps_10_10) 
avg_bx_tps_10_12 <- sum(df_bx_tx_results$tps_10_12) / sum(df_bx_tx_results$bps_10_12) 
avg_bx_tps_10_20 <- sum(df_bx_tx_results$tps_10_20) / sum(df_bx_tx_results$bps_10_20) 

# committed transaction distributions
df_hist_2 <- data.frame(df_tx_results[df_tx_results$tps_2 > 0,])
hist2 <- ggplot(df_hist_2, aes(tps_2))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 2 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_4 <- data.frame(df_tx_results[df_tx_results$tps_4 > 0,])
hist4 <- ggplot(df_hist_4, aes(tps_4))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 4 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_6 <- data.frame(df_tx_results[df_tx_results$tps_6 > 0,])
hist6 <- ggplot(df_hist_6, aes(tps_6))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 6 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_8 <- data.frame(df_tx_results[df_tx_results$tps_8 > 0,])
hist8 <- ggplot(df_hist_8, aes(tps_8))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 8 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_10 <- data.frame(df_tx_results[df_tx_results$tps_10 > 0,])
hist10 <- ggplot(df_hist_10, aes(tps_10))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 10 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_12 <- data.frame(df_tx_results[df_tx_results$tps_12 > 0,])
hist12 <- ggplot(df_hist_12, aes(tps_12))+geom_histogram(binwidth=2, fill="darkcyan")+labs(title="Target rate: 12 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_10_8 <- data.frame(df_tx_results[df_tx_results$tps_10_8 > 0,])
hist10_8 <- ggplot(df_hist_10_8, aes(tps_10_8))+geom_histogram(binwidth=10, fill="steelblue")+labs(title="Target rate: 8 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_10_10 <- data.frame(df_tx_results[df_tx_results$tps_10_10 > 0,])
hist10_10 <- ggplot(df_hist_10_10, aes(tps_10_10))+geom_histogram(binwidth=10, fill="steelblue")+labs(title="Target rate: 10 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_10_12 <- data.frame(df_tx_results[df_tx_results$tps_10_12 > 0,])
hist10_12 <- ggplot(df_hist_10_12, aes(tps_10_12))+geom_histogram(binwidth=10, fill="steelblue")+labs(title="Target rate: 12 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

df_hist_10_20 <- data.frame(df_tx_results[df_tx_results$tps_10_20 > 0,])
hist10_20 <- ggplot(df_hist_10_20, aes(tps_10_20))+geom_histogram(binwidth=10, fill="steelblue")+labs(title="Target rate: 20 tps", x="tps", y="frequency")+theme_bw()+theme(plot.title=element_text(size=11),axis.title.x=element_text(size=10),axis.title.y=element_text(size=10))

plot_grid(hist2, hist4, hist6, hist8, hist10, hist12, ncol=2)
plot_grid(hist10_8,hist10_10,hist10_12,hist10_20, ncol=2)

# line chart of 2 minute time period
df_tx_results_two_min <- df_tx_results[1020:1139,]
df_tx_results_two_min$row_num <- c(1:120)
df_melt_two_min <- melt(df_tx_results_two_min,variable.name="experiment",id="row_num")
ggplot(df_melt_two_min[df_melt_two_min$experiment %in% c("tps_4"),], aes(x=row_num,y=value, group=experiment))+geom_line(color="steelblue",show.legend = FALSE,alpha=0.4)+geom_point(size=1.5,color="steelblue",show.legend = FALSE)+geom_line(color="steelblue",show.legend = FALSE,alpha=0.5)+scale_x_time(breaks=hms(minutes=seq(0,2,0.5)), labels=label_time(format = '%M:%S'))+labs(title="Example of transactions committed in two mintute period",x="Elapsed time", y="Transactions committed (tps)")+theme_bw()+theme(plot.title=element_text(size=12,hjust=0.5,vjust=5,margin=margin(t=15)),axis.title.x=element_text(size=12,vjust=3,margin=margin(t=15)),axis.title.y=element_text(size=12,vjust=3,margin=margin(t=15)),axis.text=element_text(size=10))

# Box plots
df_melt <- melt(df_tx_results[,1:6],variable.name="experiment")
df_melt_filtered = data.frame(df_melt[df_melt$value > 0,])
ggplot(df_melt_filtered, aes(experiment,value))+geom_boxplot(color="steelblue",fill="lightblue",alpha=0.2,outlier.shape = 4,outlier.size= 1)+labs(title="Single transaction batches", x="Target tps", y="Actual tps")+scale_x_discrete(labels=c("2 tps","4 tps","6 tps","8 tps","10 tps","12 tps"))+theme_bw()+theme(plot.title = element_text(hjust=0.5),axis.title.x=element_text(margin=margin(t=10)))

df_melt <- melt(df_tx_results[,7:10],variable.name="experiment")
df_melt_filtered = data.frame(df_melt[df_melt$value > 0,])
ggplot(df_melt_filtered, aes(experiment,value))+geom_boxplot(color="steelblue",fill="lightblue",alpha=0.2,outlier.shape = 4,outlier.size= 1)+labs(title="Multiple transaction batches", x="Target tps", y="Actual tps")+scale_x_discrete(labels=c("8 tps","10 tps","12 tps","20 tps"))+theme_bw()+theme(plot.title = element_text(hjust=0.5),axis.title.x=element_text(margin=margin(t=15)))

# Analysis of maximum batches per block set to 10
tps_10_10_8 <- c(coredata(window(df_tx_time_values_xts,start="2022-05-05 15:15:00",end="2022-05-05 16:14:59")))
tps_10_10_10 <- c(coredata(window(df_tx_time_values_xts,start="2022-05-05 19:05:00",end="2022-05-05 20:04:59")))
tps_10_10_12 <- c(coredata(window(df_tx_time_values_xts,start="2022-05-05 21:15:00",end="2022-05-05 22:14:59")))
df_tx_results_max_batches <- data.frame(tps_10_10_8,tps_10_10_10,tps_10_10_12)
summary(df_tx_results_max_batches)

# Compare single transaction batches and multiple transaction batches
rate_batches <- factor(c(rep("8 tps",2),rep("10 tps",2),rep("12 tps",2)),levels=c("8 tps","10 tps","12 tps"))
type_batches <- c(rep(c("Single transaction batches","Multiple transaction batches"),3))
value_batches <- c(c(3.814,5.953),c(4.518,6.783),c(5.006,7.634))
df_compare_batches <- data.frame(rate_batches,type_batches,value_batches)

ggplot(df_compare_batches, aes(fill=fct_reorder(type_batches,value_batches,min), y=value_batches, x=rate_batches, width=0.4))+geom_bar(position="dodge",stat="identity")+scale_fill_manual(name=NULL,values=c("lightblue","steelblue"))+labs(x="Target tps",y="Mean tps",title="Committed transaction rates")+scale_y_continuous(breaks=c(2,4,6,8,10,12),limits=c(0,10))+theme_classic()+theme(legend.position=c(0.8,0.9),axis.title.y=element_text(size=14),axis.title.x=element_text(size=14,margin=margin(t=10)),axis.text=element_text(size=12),plot.title=element_text(hjust=0.5))

# Compare single transaction batches and multiple transaction batches, total blocks
rate_blocks <- factor(c(rep("8 tps",2),rep("10 tps",2),rep("12 tps",2)),levels=c("8 tps","10 tps","12 tps"))
type_blocks <- c(rep(c("Single transaction batches","Multiple transaction batches"),3))
value_blocks <- c(c(483,503),c(475,473),c(464,455))
df_compare_blocks <- data.frame(rate_blocks,type_blocks,value_blocks)

ggplot(df_compare_blocks, aes(fill=fct_reorder(type_blocks,value_blocks,max), y=value_blocks, x=rate_blocks, width=0.5))+geom_bar(position="dodge",stat="identity")+scale_fill_manual(name=NULL,values=c("lightblue","steelblue"))+labs(x="Target tps",y="Blocks",title="Number of blocks added")+scale_y_continuous(breaks=c(100,200,300,400,500,600),limits=c(0,600))+theme_classic()+theme(legend.position=c(0.8,0.9),axis.title.y=element_text(size=14),axis.title.x=element_text(size=14,margin=margin(t=10)),axis.text=element_text(size=12),plot.title=element_text(hjust=0.5))

# Compare single transaction batches and multiple transaction batches at min block size, 10 batches
rate_min_batches <- factor(c(rep("8 tps",2),rep("10 tps",2),rep("12 tps",2)),levels=c("8 tps","10 tps","12 tps"))
type_min_batches <- c(rep(c("Default batches per block (100)","Updated batches per block (10)"),6))
value_min_batches <- c(c(5.894,5.953),c(6.717,6.783),c(7.736,7.634))
df_compare_min_batches <- data.frame(rate_min_batches,type_min_batches,value_min_batches)

ggplot(df_compare_min_batches, aes(fill=type_min_batches, y=value_min_batches, x=rate_min_batches, width=0.5))+geom_bar(position="dodge",stat="identity")+scale_fill_manual(name=NULL,values=c("lightcoral","darkred"))+labs(x="Target tps",y="Mean tps",title="Committed transaction rates")+scale_y_continuous(breaks=c(2,4,6,8,10,12),limits=c(0,10))+theme_classic()+theme(legend.position=c(0.75,0.9),axis.title.y=element_text(size=14),axis.title.x=element_text(size=14,margin=margin(t=10)),axis.text=element_text(size=12),plot.title=element_text(hjust=0.5))

# Hypothesis testing
tps_10_20 <- c(coredata(window(df_tx_time_values_xts,start="2022-04-19 20:45:00",end="2022-04-19 21:44:59")))
df_tps_10_20 <- data.frame(tps_10_20)

# Raw transforms
tps_10_20_log_tf <- data.frame(tps_10_20=log10(df_tps_10_20[df_tps_10_20$tps_10_20>=0,]+1))

# Central limit theorem
sample_size <- 300
nboots <- 5000
sample_means <- numeric(nboots) 
for(i in 1:nboots) {
    sample_values <- sample(df_tps_10_20$tps_10_20,sample_size,replace=TRUE)
    sample_means[i] <- mean(sample_values) 
}   
clt <- data.frame(sample_means)
hist(sample_means)
shapiro.test(sample_means)

t.test(sqrt(sample_means),mu=sqrt(10),alternative="greater")

# Density plot of raw data
raw <- ggplot(df_tps_10_20,aes(x=tps_10_20))
    +geom_histogram(aes(y=..density..),fill="cornflowerblue")
    +geom_density(color="darkblue",fill="lightblue",alpha=0.6)
    +labs(x="Committed transaction rate (tps)",y="density",title="(a) Raw data")
    +theme_classic()
    +theme(axis.title.y=element_text(size=12,color="dimgray"),axis.title.x=element_text(size=12,margin=margin(t=10),color="dimgray"),axis.text=element_text(size=10,colour="black"),plot.title=element_text(hjust=0.5))

# Density plot of raw data with transform
raw_transform <- ggplot(tps_10_20_log_tf,aes(x=tps_10_20))
    +geom_histogram(aes(y=..density..),fill="cornflowerblue")
    +geom_density(color="darkblue",fill="lightblue",alpha=0.6)
    +labs(x=expression(log[10](Committed~transaction~rate~(tps))),y="density",title="(b) Raw data, log transform")
    +theme_classic()
    +theme(axis.title.y=element_text(size=12,color="dimgray"),axis.title.x=element_text(size=12,margin=margin(t=10),color="dimgray"),axis.text=element_text(size=10,colour="black"),plot.title=element_text(hjust=0.5))

# Density plot after central limit theorem
raw_clt <- ggplot(clt,aes(x=sample_means))
    +geom_histogram(aes(y=..density..),binwidth=0.5,fill="cornflowerblue")
    +geom_density(color="darkblue",fill="lightblue",alpha=0.6)
    +labs(x="Committed transaction rate (tps)",y="density",title="(c) Central limit theorem")
    +theme_classic()
    +theme(axis.title.y=element_text(size=12,color="dimgray"),axis.title.x=element_text(size=12,margin=margin(t=10),color="dimgray"),axis.text=element_text(size=10,colour="black"),plot.title=element_text(hjust=0.5))

# Density plot of central limit theorem with transform
raw_clt_transform <- ggplot(clt,aes(x=sqrt(sample_means)))
    +geom_histogram(aes(y=..density..),fill="cornflowerblue")
    +geom_density(color="darkblue",fill="lightblue",alpha=0.6)
    +labs(x="sqrt(Committed transaction rate (tps))",y="density",title="(d) Central limit theorem, square root transform")
    +theme_classic()
    +theme(axis.title.y=element_text(size=12,color="dimgray"),axis.title.x=element_text(size=12,margin=margin(t=10),color="dimgray"),axis.text=element_text(size=10,colour="black"),plot.title=element_text(hjust=0.5))

plot_grid(raw,raw_transform,raw_clt,raw_clt_transform,ncol=2)
