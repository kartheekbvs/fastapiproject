from fastapi import APIRouter, HTTPException, UploadFile, Form
from pydantic import BaseModel
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression # Import LogisticRegression
router = APIRouter()
# 1. Load the dataset
df = pd.read_csv("app/BostonHousing.csv")

# 2. Separate features (X) and target (Y)
X = df.iloc[:, :-1]
Y = df.iloc[:, -1]

# 3. Split data into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=1)

# 4. Define features to remove based on previous requests and Lasso analysis
columns_to_drop = ['age', 'indus', 'rad', 'tax']

# 5. Remove features from x_train and x_test
x_train = x_train.drop(columns=columns_to_drop)
x_test = x_test.drop(columns=columns_to_drop)
print(f"x_train columns after removing {columns_to_drop}:", x_train.columns)
print(f"x_test columns after removing {columns_to_drop}:", x_test.columns)

# 6. Initialize and process the 'data' array for new prediction
# This array corresponds to the original X columns before any drops
original_data_array = np.array([
    0.06905, 0.0, 2.18, 0, 0.458, 7.147, 54.2, 6.0622, 3, 222, 18.7, 396.90, 5.33
])

# Create a pandas Series from the original_data_array with appropriate column names for easy dropping
data_series = pd.Series(original_data_array, index=X.columns)

# Drop the same columns from the data_series to get the processed data as a Series with feature names
data_processed = data_series.drop(columns_to_drop)

# Convert to a DataFrame with one row for prediction, retaining feature names
data_for_prediction_df = data_processed.to_frame().T
print("Data for prediction after feature removal:\n", data_for_prediction_df)

# 7. Outlier removal on x_train and y_train
# Combine x_train and y_train for consistent filtering
train_data = pd.concat([x_train, y_train], axis=1)
original_train_data_shape = train_data.shape[0]

outlier_mask = pd.Series(True, index=train_data.index)

for col in x_train.columns:
    q1 = train_data[col].quantile(0.25)
    q3 = train_data[col].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    outlier_mask = outlier_mask & (train_data[col] >= lower_bound) & (train_data[col] <= upper_bound)

train_data_cleaned = train_data[outlier_mask]
x_train_cleaned = train_data_cleaned[x_train.columns]
y_train_cleaned = train_data_cleaned[y_train.name]

print(f"Original number of training samples: {original_train_data_shape}")
print(f"Number of training samples after outlier removal: {x_train_cleaned.shape[0]}")

# 8. Linear Regression Model Training and Prediction
model = LinearRegression()
model.fit(x_train_cleaned, y_train_cleaned)
print("Linear Regression model fitted successfully with cleaned data.")

def prediction(data_input_series):
  # data_input_series may already be reduced to the trained feature set,
  # or it may contain the original full feature set.
  data_processed_for_func = data_input_series.drop(columns_to_drop, errors="ignore")
  # Convert to a DataFrame with one row for prediction, retaining feature names
  predicted_value = model.predict(data_processed_for_func.to_frame().T)
  return predicted_value

# Make a new prediction with the fully processed data array
# Now use the DataFrame `data_for_prediction_df` which has feature names
final_prediction_lr = model.predict(data_for_prediction_df)
print(f"Final prediction with Linear Regression after all removals and outlier handling: {final_prediction_lr}")

# Evaluate Linear Regression model
lr_train_score = model.score(x_train_cleaned, y_train_cleaned)
lr_test_score = model.score(x_test, y_test)
print(f"Linear Regression Train Score: {lr_train_score:.4f}")
print(f"Linear Regression Test Score: {lr_test_score:.4f}")

y_pred_lr = model.predict(x_test)
print("Linear Regression Metrics:")
print(f"  MAE: {mean_absolute_error(y_test, y_pred_lr):.4f}")
print(f"  MSE: {mean_squared_error(y_test, y_pred_lr):.4f}")
print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_lr)):.4f}")
print(f"  R2: {r2_score(y_test, y_pred_lr):.4f}")

# 9. Lasso Regression Model Training and Coefficients
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train_cleaned) # Scale cleaned training data
x_test_scaled = scaler.transform(x_test) # Scale test data

lasso = Lasso(alpha=0.1)
lasso.fit(x_train_scaled, y_train_cleaned) # Fit Lasso with cleaned and scaled data

print("\nLasso model refitted successfully. Final coefficients:")
for col, coef in zip(x_train_cleaned.columns, lasso.coef_):
    print(f"  {col}: {coef:.4f}")

# Evaluate Lasso model
lasso_train_score = lasso.score(x_train_scaled, y_train_cleaned)
lasso_test_score = lasso.score(x_test_scaled, y_test)
print(f"Lasso Regression Train Score: {lasso_train_score:.4f}")
print(f"Lasso Regression Test Score: {lasso_test_score:.4f}")

y_pred_lasso = lasso.predict(x_test_scaled)
print("Lasso Regression Metrics:")
print(f"  MAE: {mean_absolute_error(y_test, y_pred_lasso):.4f}")
print(f"  MSE: {mean_squared_error(y_test, y_pred_lasso):.4f}")
print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_lasso)):.4f}")
print(f"  R2: {r2_score(y_test, y_pred_lasso):.4f}")

def logistic(text):
    le = LabelEncoder()
    vectorizer=CountVectorizer()
    df=pd.read_csv("app/spam_or_not_spam.csv")
    df["email"] = df["email"].fillna("")
    x_train,x_test,y_train,y_test = train_test_split(df["email"],df["label"],test_size=0.2)
    x_train=vectorizer.fit_transform(x_train)
    x_test=vectorizer.transform(x_test)

# Define the new text you want to predict
    new_text_to_predict = pd.Series([text])

# Vectorize the new text
    new_email_vectorized = vectorizer.transform(new_text_to_predict.fillna(""))

# Initialize the model before fitting
    model=LogisticRegression() # Initialize the model

# Re-fit the model with the current x_train to ensure feature count consistency
# This step should ideally be done once after the final x_train is prepared,
# but is included here for self-contained execution with the new text.
    model.fit(x_train,y_train)

# Make the prediction
    prediction = model.predict(new_email_vectorized)
    predicted_label = int(prediction[0])
    print(f"Predicted label: {predicted_label}")
    return predicted_label
@router.get("/predict")
def predict_get(crim: float, zn: float, chas: float, nox: float, rm: float, dis: float, ptratio: float, black: float, lstat: float):
    data = [crim, zn, chas, nox, rm, dis, ptratio, black, lstat]
    data_series = pd.Series(data, index=x_train.columns)
    prediction_result = prediction(data_series)
    return {"predicted_value": prediction_result.tolist()}

@router.post("/predict")
def predict_post(
    crim: float = Form(...),
    zn: float = Form(...),
    chas: float = Form(...),
    nox: float = Form(...),
    rm: float = Form(...),
    dis: float = Form(...),
    ptratio: float = Form(...),
    black: float = Form(...),
    lstat: float = Form(...),
):
    data = [crim, zn, chas, nox, rm, dis, ptratio, black, lstat]
    data_series = pd.Series(data, index=x_train.columns)
    prediction_result = prediction(data_series)
    final_r = sigmoid(prediction_result)
    return {"predicted_value": final_r.tolist()}
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

@router.post("/predict1")
def predict1(text: str = Form(...)):
    output = logistic(text)
    if(output == 1):
        ans="spam"
    else:
        ans="Not spam"
    return {"You mail is ": ans}



