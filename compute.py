import numpy as np
from sklearn.metrics import roc_auc_score, recall_score, brier_score_loss

from calibration_framework import CalibrationFramework

cf = CalibrationFramework()
# (
#     select_probability,
#     calibrationdiagnosis,
#     classwise_calibration,
# )

def var_brier_score(y_test, y_proba):
  val = np.mean(y_proba**4)
  val -= 4*np.mean(y_proba**3 * y_test)
  val += 6*np.mean(y_proba**2 * y_test)
  val -= 4*np.mean(y_proba * y_test)
  val += np.mean(y_test) 
  val -= brier_score_loss(y_test, y_proba)**2
  return val

def var_auc(auc, num_pos, num_neg):
  prop = num_pos/(num_pos + num_neg)
  n = num_pos + num_neg
  se = np.sqrt(auc*(1-auc)*(1 + (n/2 - 1)*(1 - auc)/(2- auc) + (n/2 -1)*auc/(1+auc))/(n**2*prop*(1-prop)))
  return se**2

def var_nb(sens, spec, prop, n, th=0.5):
  w = (1-prop)/prop*th/(1-th)
  return 1/n * ( sens*(1-sens)/prop + w**2 * spec*(1-spec)/(1-prop) + w**2 * (1-spec)**2/(prop*(1-prop)))

def nb(y_true, y_proba, th=0.5):
  prop = len(y_true[y_true == 1])/len(y_true)
  y_pred = (y_proba >= th).astype(int)
  sens = recall_score(y_true, y_pred)
  spec = recall_score(y_true, y_pred, pos_label=0)
  return (sens*prop - (1-spec)*(1-prop)*th/(1-th))/prop

def wu(y_true, y_proba, ths=None, relevances=None):
  if ths is None and relevances is None:
    return nb(y_true, y_proba)
  
  if np.isscalar(ths) and relevances is None:
    return nb(y_true, y_proba, ths)
  
  if relevances is None:
    relevances = np.ones(y_proba.shape)
  
  if ths is None:
    ths = np.ones(y_proba.shape)*0.5
  elif np.isscalar(ths):
    ths = np.ones(y_proba.shape)*ths


  if len(ths) != len(y_true):
    raise ValueError("If not scalar or None, ths should have the same length as y_true")
  if len(relevances) != len(y_true):
    raise ValueError("If not None, relevances should have the same length as y_true")


  pos_idx = y_true == 1
  rs = np.sum(relevances[pos_idx])
  pp = y_proba >= ths
  tp = np.logical_and(pos_idx, pp)
  fp = np.logical_and(np.logical_not(pos_idx), pp)
  return np.sum(tp*relevances)/rs - np.sum(ths/(1-ths)*fp*relevances)/rs

def mss_auc(auc, prop, target_se = 0.0255):
  for n in range(10, 1000000):
    se = np.sqrt(auc*(1-auc)*(1 + (n/2 - 1)*(1 - auc)/(2- auc) + (n/2 -1)*auc/(1+auc))/(n**2*prop*(1-prop)))
    if se <= target_se:
      return n

def mss_nb(sens, spec, prop, th=0.5, target_se = 0.051):
  w = (1-prop)/prop*th/(1-th)
  return 1/target_se**2 * ( sens*(1-sens)/prop + w**2 * spec*(1-spec)/(1-prop) + w**2 * (1-spec)**2/(prop*(1-prop)))

def mss_brier(var_briers):
  return (2*1.96*np.sqrt(var_briers)/0.05)**2


def compute(y_test, y_proba, ths, rels, options):
  
    o = options

    y_pred = np.array([1 if y > 0.5 else 0 for y in y_proba])
    num_pos = len(y_pred[y_pred == 1])
    ths = 0.5 if (ths is None) else np.mean(ths)

    sens = recall_score(y_test, y_pred)
    spec = recall_score(y_test, y_pred, pos_label=0)
    auc_val = roc_auc_score(y_test, y_proba)
    
    if o.utility_metric  == "wu":
      nb_val = wu(y_test, y_proba, ths, rels)
    elif o.utility_metric == "snb":
      nb_val = nb(y_test, y_proba, ths, )
      
    if o.discrimination_metric == "bas":
      auc_val = (sens + spec)/2

    calib_val = 0

    if o.calibration_metric == "brier":
      brier_val = brier_score_loss(y_test, y_proba)
      calib_val = brier_val
    elif o.calibration_metric == "eci":
      y_eci = np.zeros((y_proba.shape[0],2))
      y_eci[:, 1] = y_proba
      y_eci[:, 0] = 1 - y_proba
      classes_scores = cf.select_probability(y_test, y_eci, y_pred)

      strategy = 5

      rs, _ = cf.calibrationdiagnosis(
          classes_scores, strategy=strategy, undersampling=False
      )

      global_metrics = cf.classwise_calibration(rs)

      eci = global_metrics["ec_g"]
      calib_val = eci

    var_brier_val = var_brier_score(y_test, y_proba)
    var_auc_val = var_auc(auc_val, num_pos, len(y_test) - num_pos)
    if o.discrimination_metric == "bas":
      var_auc_val = auc_val*(1-auc_val)
    var_nb_val = var_nb(sens, spec, num_pos/len(y_test), len(y_test), ths)

    size_auc = mss_auc(auc_val, num_pos/len(y_test))
    size_nb = mss_nb(sens, spec, num_pos/len(y_test), ths)
    size_brier = mss_brier(var_brier_val)

    return auc_val, nb_val, calib_val, len(y_test), size_auc, size_nb, size_brier, var_auc_val, var_nb_val, var_brier_val 