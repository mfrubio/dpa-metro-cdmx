from train.interquartile_range import interquartile_range
from train.ParametrizedLabelTest import ParametrizedLabelTest


class LabelTest(ParametrizedLabelTest):
    def test_label_creation(self):
        intquar_ran = interquartile_range()
        label_df = intquar_ran.create_label(intquar_ran.join_range(self.cleaned_data, intquar_ran.calculate_range(self.cleaned_data)))
        distinct_labels = label_df['label'].unique()

        print("aqui"+str(distinct_labels))
        self.assertListEqual(distinct_labels, range(1, 4))
