require('ggplot2')
require('GGally')

scatter_matrix = function(data, path) {
	
	data$aLL_tLL = data$trans_type_aLLtLL
	data$tLL_aSS = data$trans_type_tLLaSS
	data$aLL_aSS = data$trans_type_aLLaSS
	data$aSS_tSS = data$trans_type_aSStSS
	data$tLL_tSS = data$trans_type_tLLtSS
	data$aLL_tSS = data$trans_type_aLLtSS	
	
	png(file=path, width=400, height=400)
	pairs(~	aLL_tLL +
			tLL_aSS +
			aLL_aSS +
			aSS_tSS +
			tLL_tSS +
			aLL_tSS,
			data=data,
			col=factor(data$cluster2),
			pch=16)

	dev.off()
}