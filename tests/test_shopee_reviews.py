import unittest

import pandas as pd

from src.shopee_reviews import build_reviews_dataframe, extract_ids_from_url


class ShopeeReviewHelpersTests(unittest.TestCase):
    def test_extract_ids_from_standard_item_link(self):
        shop_id, item_id = extract_ids_from_url(
            "https://shopee.vn/Tai-nghe-khong-day-i.123456789.987654321"
        )

        self.assertEqual((shop_id, item_id), (123456789, 987654321))

    def test_extract_ids_from_product_path_link(self):
        shop_id, item_id = extract_ids_from_url(
            "https://shopee.vn/product/123456789/987654321?uls_trackid=abc"
        )

        self.assertEqual((shop_id, item_id), (123456789, 987654321))

    def test_build_reviews_dataframe_filters_blank_comments_and_duplicates(self):
        dataframe = build_reviews_dataframe(
            ratings=[
                {
                    "cmtid": 1,
                    "comment": "Giao nhanh, dong goi ky.",
                    "rating_star": 5,
                    "author_username": "user_a",
                    "ctime": 1713200000,
                },
                {
                    "cmtid": 1,
                    "comment": "Giao nhanh, dong goi ky.",
                    "rating_star": 5,
                    "author_username": "user_a",
                    "ctime": 1713200000,
                },
                {
                    "cmtid": 2,
                    "comment": "   ",
                    "rating_star": 3,
                    "author_username": "user_b",
                    "ctime": 1713200100,
                },
            ],
            shop_id=123,
            item_id=456,
            source_url="https://shopee.vn/product/123/456",
        )

        self.assertEqual(len(dataframe), 1)
        self.assertEqual(dataframe.loc[0, "comment"], "Giao nhanh, dong goi ky.")
        self.assertEqual(dataframe.loc[0, "shop_id"], 123)
        self.assertEqual(dataframe.loc[0, "item_id"], 456)
        self.assertTrue(pd.notna(dataframe.loc[0, "created_at"]))


if __name__ == "__main__":
    unittest.main()
