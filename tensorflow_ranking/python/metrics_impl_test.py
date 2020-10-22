# Copyright 2021 The TensorFlow Ranking Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for ranking metrics implementation."""

import math
import tensorflow as tf

from tensorflow_ranking.python import metrics_impl


def log2p1(x):
  return math.log2(1. + x)


class MRRMetricTest(tf.test.TestCase):

  def test_mrr_should_be_single_value(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1. / 2.]])

  def test_mrr_should_be_0_when_no_rel_item(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_mrr_should_be_0_when_no_rel_item_in_topn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric = metrics_impl.MRRMetric(name=None, topn=1)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_mrr_should_handle_topn(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [3., 2., 1.], [3., 2., 1.]]
      labels = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]

      metric_top1 = metrics_impl.MRRMetric(name=None, topn=1)
      metric_top2 = metrics_impl.MRRMetric(name=None, topn=2)
      metric_top6 = metrics_impl.MRRMetric(name=None, topn=6)
      output_top1, _ = metric_top1.compute(labels, scores, None)
      output_top2, _ = metric_top2.compute(labels, scores, None)
      output_top6, _ = metric_top6.compute(labels, scores, None)

      self.assertAllClose(output_top1, [[1.], [0.], [0.]])
      self.assertAllClose(output_top2, [[1.], [1. / 2.], [0.]])
      self.assertAllClose(output_top6, [[1.], [1. / 2.], [1. / 3.]])

  def test_mrr_should_ignore_padded_labels(self):
    with tf.Graph().as_default():
      scores = [[1., 2., 3.]]
      labels = [[0., 1., -1.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1.]])

  def test_mrr_should_give_a_value_for_each_list_in_batch_inputs(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 2., 3.]]
      labels = [[0., 0., 1.], [0., 1., 1.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1. / 2.], [1.]])

  def test_mrr_weights_should_be_average_weight_of_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 2., 3.]]
      labels = [[1., 0., 0.], [0., 1., 1.]]
      weights = [[2., 5., 1.], [1., 2., 3.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[2.], [(2. + 3.) / 2.]])

  def test_mrr_weights_should_be_0_without_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]
      weights = [[2., 5., 1.]]

      metric = metrics_impl.MRRMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[0.]])

  def test_mrr_weights_should_be_regardless_of_topn(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [1., 3., 2.]]
      labels = [[1., 0., 1.], [0., 1., 1.]]
      weights = [[2., 0., 5.], [1., 4., 2.]]

      metric = metrics_impl.MRRMetric(name=None, topn=2)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(5. + 2.) / 2.], [(2. + 4.) / 2.]])


class ARPMetricTest(tf.test.TestCase):

  def test_arp_should_give_output_and_weight_vectors(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric = metrics_impl.ARPMetric(name=None)
      output, output_weights = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1., 2., 3.]])
      self.assertAllClose(output_weights, [[0., 1., 0.]])

  def test_arp_should_give_output_and_weight_vectors_per_list(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 2., 3.]]
      labels = [[0., 0., 1.], [0., 1., 2.]]

      metric = metrics_impl.ARPMetric(name=None)
      output, output_weights = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1., 2., 3.], [1., 2., 3.]])
      self.assertAllClose(output_weights, [[0., 1., 0.], [2., 1., 0.]])

  def test_arp_should_have_0_weight_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.ARPMetric(name=None)
      output, output_weights = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1., 2., 3.]])
      self.assertAllClose(output_weights, [[0., 0., 0.]])

  def test_arp_should_ignore_padded_items(self):
    with tf.Graph().as_default():
      scores = [[1., 5., 4., 3., 2.]]
      labels = [[1., -1., 1., -1., 0.]]

      metric = metrics_impl.ARPMetric(name=None)
      output, output_weights = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1., 2., 3., 4., 5.]])
      self.assertAllClose(output_weights, [[1., 0., 1., 0., 0.]])

  def test_arp_should_multiply_labels_with_weights(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 2., 3.]]
      labels = [[0., 0., 1.], [0., 1., 2.]]
      weights = [[1., 2., 3.], [4., 5., 6.]]

      metric = metrics_impl.ARPMetric(name=None)
      output, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output, [[1., 2., 3.], [1., 2., 3.]])
      self.assertAllClose(output_weights, [[0., 3., 0.], [12., 5., 0.]])


class RecallMetricTest(tf.test.TestCase):

  def test_recall_should_be_single_value(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric = metrics_impl.RecallMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1.]])

  def test_recall_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.RecallMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_recall_should_handle_topn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric_top1 = metrics_impl.RecallMetric(name=None, topn=1)
      metric_top2 = metrics_impl.RecallMetric(name=None, topn=2)
      metric_top6 = metrics_impl.RecallMetric(name=None, topn=6)
      output_top1, _ = metric_top1.compute(labels, scores, None)
      output_top2, _ = metric_top2.compute(labels, scores, None)
      output_top6, _ = metric_top6.compute(labels, scores, None)

      self.assertAllClose(output_top1, [[0.]])
      self.assertAllClose(output_top2, [[1.]])
      self.assertAllClose(output_top6, [[1.]])

  def test_recall_should_be_single_value_per_list(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 3., 4.]]
      labels = [[1., 0., 1.], [0., 1., 1.]]

      metric = metrics_impl.RecallMetric(name=None, topn=2)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1. / 2.], [1.]])

  def test_recall_weights_should_be_avg_of_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 1., 0.]]
      weights = [[3., 9., 2.]]

      metric = metrics_impl.RecallMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(3. + 9.) / 2.]])

  def test_recall_weights_should_ignore_graded_relevance(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[4., 0., 2.]]
      weights = [[3., 9., 2.]]

      metric = metrics_impl.RecallMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(3. + 2.) / 2.]])

  def test_recall_weights_should_ignore_topn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 1., 0.]]
      weights = [[3., 9., 2.]]

      metric = metrics_impl.RecallMetric(name=None, topn=1)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(3. + 9.) / 2.]])

  def test_recall_weights_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.RecallMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, None)

      self.assertAllClose(output_weights, [[0.]])


class PrecisionMetricTest(tf.test.TestCase):

  def test_precision_should_be_single_value(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 1.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[1. / 3.]])

  def test_precision_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_precision_should_be_single_value_per_list(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2., 4.], [4., 1., 3., 2.]]
      labels = [[0., 0., 1., 1.], [0., 0., 1., 0.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[2. / 4.], [1. / 4.]])

  def test_precision_should_handle_topn(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [3., 2., 1.], [3., 2., 1.]]
      labels = [[1., 0., 1.], [0., 1., 0.], [0., 0., 1.]]

      metric_top1 = metrics_impl.PrecisionMetric(name=None, topn=1)
      metric_top2 = metrics_impl.PrecisionMetric(name=None, topn=2)
      metric_top6 = metrics_impl.PrecisionMetric(name=None, topn=6)
      output_top1, _ = metric_top1.compute(labels, scores, None)
      output_top2, _ = metric_top2.compute(labels, scores, None)
      output_top6, _ = metric_top6.compute(labels, scores, None)

      self.assertAllClose(output_top1, [[1. / 1.], [0. / 1.], [0. / 1.]])
      self.assertAllClose(output_top2, [[1. / 2.], [1. / 2.], [0. / 2.]])
      self.assertAllClose(output_top6, [[2. / 3.], [1. / 3.], [1. / 3.]])

  def test_precision_weights_should_be_avg_of_weights_of_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 0., 2.]]
      weights = [[13., 7., 29.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(13. + 29.) / 2.]])

  def test_precision_weights_should_ignore_topn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 1., 0.]]
      weights = [[3., 7., 15.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=1)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(3. + 7.) / 2.]])

  def test_precision_weights_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]
      weights = [[3., 7., 15.]]

      metric = metrics_impl.PrecisionMetric(name=None, topn=1)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[0.]])


class MeanAveragePrecisionMetricTest(tf.test.TestCase):

  def test_map_should_be_single_value(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.]]
      labels = [[0., 1., 0.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[(1. / 2.) / 1.]])

  def test_map_should_treat_graded_relevance_as_binary_relevance(self):
    with tf.Graph().as_default():
      scores = [[3., 4., 1., 2.]]
      labels = [[0., 2., 1., 3.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[(1. + 2. / 3. + 3. / 4.) / 3.]])

  def test_map_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_map_should_be_single_value_per_list(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.], [1., 3., 2.]]
      labels = [[0., 0., 1.], [0., 1., 1.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[(1. / 2.) / 1.],
                                   [(1. / 1. + 2. / 2.) / 2.]])

  def test_map_should_handle_topn(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [3., 2., 1.], [3., 2., 1.]]
      labels = [[1., 0., 2.], [0., 1., 0.], [0., 0., 1.]]

      metric_top1 = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=1)
      metric_top2 = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=2)
      metric_top6 = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=6)
      output_top1, _ = metric_top1.compute(labels, scores, None)
      output_top2, _ = metric_top2.compute(labels, scores, None)
      output_top6, _ = metric_top6.compute(labels, scores, None)

      self.assertAllClose(output_top1, [[1. / 2.],
                                        [0. / 1.],
                                        [0. / 1.]])
      self.assertAllClose(output_top2, [[1. / 2.],
                                        [(1. / 2.) / 1.],
                                        [0. / 1.]])
      self.assertAllClose(output_top6, [[(1. + 2. / 3.) / 2.],
                                        [(1. / 2.) / 1.],
                                        [(1. / 3.) / 1.]])

  def test_map_weights_should_be_avg_of_weights_of_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 0., 2.]]
      weights = [[13., 7., 29.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(13. + 29.) / 2.]])

  def test_map_weights_should_ignore_topn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 1., 0.]]
      weights = [[3., 7., 15.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=1)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[(3. + 7.) / 2.]])

  def test_map_weights_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]
      weights = [[3., 7., 15.]]

      metric = metrics_impl.MeanAveragePrecisionMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[0.]])


class NDCGMetricTest(tf.test.TestCase):

  def test_ndcg_should_be_single_value(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.]]
      labels = [[0., 1., 0.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      dcg = 1. / log2p1(2.)
      max_dcg = 1. / log2p1(1.)
      self.assertAllClose(output, [[dcg / max_dcg]])

  def test_ndcg_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.]]
      labels = [[0., 0., 0.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      self.assertAllClose(output, [[0.]])

  def test_ndcg_should_operate_on_graded_relevance(self):
    with tf.Graph().as_default():
      scores = [[4., 3., 2., 1.]]
      labels = [[0., 3., 1., 0.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      dcg = (2. ** 3. - 1.) / log2p1(2.) + 1. / log2p1(3.)
      max_dcg = (2. ** 3. - 1.) / log2p1(1.) + 1. / log2p1(2.)
      self.assertAllClose(output, [[dcg / max_dcg]])

  def test_ndcg_should_operate_on_graded_relevance_with_custom_gain_fn(self):
    with tf.Graph().as_default():
      scores = [[4., 3., 2., 1.]]
      labels = [[0., 3., 1., 0.]]
      gain_fn = lambda label: label / 2.

      metric = metrics_impl.NDCGMetric(name=None, topn=None, gain_fn=gain_fn)
      output, _ = metric.compute(labels, scores, None)

      dcg = (3. / 2.) / log2p1(2.) + (1. / 2.) / log2p1(3.)
      max_dcg = (3. / 2.) / log2p1(1.) + (1. / 2.) / log2p1(2.)
      self.assertAllClose(output, [[dcg / max_dcg]])

  def test_ndcg_should_use_custom_rank_discount_fn(self):
    with tf.Graph().as_default():
      scores = [[4., 3., 2., 1.]]
      labels = [[0., 3., 1., 0.]]
      rank_discount_fn = lambda rank: 1.0 / (rank + 10.0)

      metric = metrics_impl.NDCGMetric(name=None, topn=None,
                                       rank_discount_fn=rank_discount_fn)
      output, _ = metric.compute(labels, scores, None)

      dcg = (2. ** 3. - 1.) / (2. + 10.) + 1. / (3. + 10.)
      max_dcg = (2. ** 3. - 1.) / (1. + 10.) + 1. / (2. + 10.)
      self.assertAllClose(output, [[dcg / max_dcg]])

  def test_ndcg_should_ignore_padded_items(self):
    with tf.Graph().as_default():
      scores = [[1., 4., 3., 2.]]
      labels = [[2., -1., 1., 0.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      dcg = (2. ** 2. - 1.) / log2p1(3.) + 1. / log2p1(1.)
      max_dcg = (2. ** 2. - 1.) / log2p1(1.) + 1. / log2p1(2.)
      self.assertAllClose(output, [[dcg / max_dcg]])

  def test_ndcg_should_be_single_value_per_list(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [3., 1., 2.]]
      labels = [[0., 1., 0.], [1., 1., 0.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      output, _ = metric.compute(labels, scores, None)

      dcg = [1. / log2p1(2.), 1. / log2p1(1.) + 1. / log2p1(3.)]
      max_dcg = [1. / log2p1(1.), 1. / log2p1(1.) + 1. / log2p1(2.)]
      self.assertAllClose(output,
                          [[dcg[0] / max_dcg[0]], [dcg[1] / max_dcg[1]]])

  def test_ndcg_should_handle_topn(self):
    with tf.Graph().as_default():
      scores = [[3., 2., 1.], [3., 2., 1.], [3., 2., 1.]]
      labels = [[1., 0., 2.], [0., 1., 0.], [0., 0., 1.]]

      metric_top1 = metrics_impl.NDCGMetric(name=None, topn=1)
      metric_top2 = metrics_impl.NDCGMetric(name=None, topn=2)
      metric_top6 = metrics_impl.NDCGMetric(name=None, topn=6)
      output_top1, _ = metric_top1.compute(labels, scores, None)
      output_top2, _ = metric_top2.compute(labels, scores, None)
      output_top6, _ = metric_top6.compute(labels, scores, None)

      max_dcg_top1 = [(2. ** 2. - 1.) / log2p1(1.),
                      1. / log2p1(1.),
                      1. / log2p1(1.)]
      max_dcg = [(2. ** 2. - 1.) / log2p1(1.) + 1. / log2p1(2.),
                 1. / log2p1(1.),
                 1. / log2p1(1.)]

      self.assertAllClose(output_top1,
                          [[(1. / log2p1(1.)) / max_dcg_top1[0]],
                           [0. / max_dcg_top1[1]],
                           [0. / max_dcg_top1[2]]])
      self.assertAllClose(output_top2,
                          [[(1. / log2p1(1.)) / max_dcg[0]],
                           [(1. / log2p1(2.)) / max_dcg[1]],
                           [0. / max_dcg[2]]])
      self.assertAllClose(output_top6,
                          [[(1. / log2p1(1.) + (2. ** 2. - 1.) / log2p1(3.)) /
                            max_dcg[0]],
                           [(1. / log2p1(2.)) / max_dcg[1]],
                           [(1. / log2p1(3.)) / max_dcg[2]]])

  def test_ndcg_weights_should_be_average_of_weighted_gain(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 0., 2.]]
      weights = [[3., 7., 9.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(
          output_weights,
          [[(1. * 3. + (2. ** 2. - 1.) * 9.) / (1. + (2. ** 2. - 1.))]])

  def test_ndcg_weights_should_be_0_when_no_rel_items(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[0., 0., 0.]]
      weights = [[2., 4., 4.]]

      metric = metrics_impl.NDCGMetric(name=None, topn=None)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(output_weights, [[0.]])

  def test_ndcg_weights_should_use_custom_gain_fn(self):
    with tf.Graph().as_default():
      scores = [[1., 3., 2.]]
      labels = [[1., 0., 2.]]
      weights = [[3., 7., 9.]]
      gain_fn = lambda label: label + 5.

      metric = metrics_impl.NDCGMetric(name=None, topn=None, gain_fn=gain_fn)
      _, output_weights = metric.compute(labels, scores, weights)

      self.assertAllClose(
          output_weights,
          [[((1. + 5.) * 3. + (0. + 5.) * 7. + (2. + 5.) * 9.) /
            ((1. + 5.) + (0. + 5.) + (2. + 5.))]])


if __name__ == '__main__':
  tf.compat.v1.enable_v2_behavior()
  tf.test.main()
