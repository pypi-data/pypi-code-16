import numpy as np

#Threshold is the cut-off value for the eigen values of the covariance matrix
# This value must be between 0 and 1

def PCA(Matrix, Threshold):

	#gettning covariance matrix and eigens
	cov_mat = np.cov(Matrix)
	eig_val, eig_vect = np.linalg.eig(cov_mat)

	#sorting the eigen values and creating a threshold cutoff
	sorted_val = reversed(np.sort(eig_val))
	eig_sum = np.sum(eig_val)
	threshold_value = eig_sum*Threshold

	#creating another set to index with
	thresh_set =[]
	number = 0

	for x in sorted_val:
		if number < threshold_value:
			thresh_set.append(x)
			number = number + x

	indices = []
	#indexing position in original eigenvalue vector
	for i in thresh_set:
		index = np.where(eig_val==i)

		#lets make it a vector of indices
		for j in index[0]:
			indices.append(int(j))

	#A matrix for the eigen vectors that we want to keep
	signif_eigs = []
	for i in indices:
		vector = eig_vect[:,i]

		#we want the norm of the eigen vector.
		v_norm = np.linalg.norm(vector)
		u_vector = np.divide(vector,v_norm)

		vector = np.ndarray.tolist(u_vector)
		signif_eigs.append(vector)
	
	#let's transpose this matrix for multiplication
	signif_eigs = np.array(signif_eigs)

	#let's also transpose the data matrix because we have to for some reason?
	New_Matrix = Matrix.transpose()

	New_Data = np.inner(New_Matrix,signif_eigs)



	return New_Data
