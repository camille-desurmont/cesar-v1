# Prediction contract: the agreement on what goes in and what comes out of the model.
#
# The "contract" is the list of features the model expects (names, order, types) 
# and what it returns. Without it, the training code might use columns A,B,C, the API might
# send B,A,D, and predictions would be wrong or break. By sharing one contract (request shape,
# response shape, and an on-disk file next to the model that records feature names and version),
# the training pipeline, the API, the batch CLI, and the single-record CLI all stay in sync. This
# package holds that contract: request/response schemas and the on-disk contract format.
