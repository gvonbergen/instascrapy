"""This file includes all test cases for pipelines"""
import time

import pytest

from instascrapy.items import IGLoader, IGUser, IGPost
from instascrapy.pipelines import MongoDBPipeline


@pytest.fixture()
def mongodb_pipeline(mongodb):
    mongo_pipe = MongoDBPipeline(mongo_uri="localhost",
                                 mongo_db="instascrapy",
                                 mongo_collection="dev",
                                 mongo_user="None",
                                 mongo_password="None")
    mongo_pipe.collection = mongodb.pipeline

    return mongo_pipe


class TestIGUserMongo:
    @pytest.fixture()
    def iguser(self):
        loader = IGLoader(item=IGUser())
        loader.add_value("username", "testuser")
        loader.add_value("id", "12345")
        loader.add_value("id", "111")
        loader.add_value("last_posts", "XAB")
        loader.add_value("last_posts", "XBB")
        loader.add_value("retrieved_at_time", time.time())
        loader.add_value("user_json", {"biography": "My Biography",
                                       "edge_followed_by": {"count": 4}}
                         )
        loader.add_value("profile_pic_url", "http://test.ch")
        loader.add_value("full_name", "Test User")

        return loader.load_item()

    @pytest.fixture()
    def write_iguser(self, mongodb_pipeline, iguser):
        spider = None
        mongodb_pipeline.process_item(iguser, spider)

        return mongodb_pipeline

    @pytest.fixture()
    def iguser_main(self, write_iguser):
        return write_iguser.collection.find_one({"pk": "US#testuser", "sk": {"$regex": "USER"}})

    def test_iguser_main_length(self, iguser_main):
        assert len(iguser_main) == 5

    def test_iguser_main_pk(self, iguser_main):
        assert iguser_main["pk"] == "US#testuser"

    def test_iguser_main_discovered_integer(self, iguser_main):
        assert isinstance(iguser_main["discovered_at_time"], int)

    def test_iguser_main_discovered_number(self, iguser_main):
        assert iguser_main["discovered_at_time"] > 1583055697

    def test_iguser_main_retrieved_integer(self, iguser_main):
        assert isinstance(iguser_main["retrieved_at_time"], int)

    def test_iguser_main_assert_times(self, iguser_main):
        assert iguser_main["retrieved_at_time"] >= iguser_main["retrieved_at_time"]

    @pytest.fixture()
    def iguser_update(self, write_iguser):
        return write_iguser.collection.find_one({"pk": "US#testuser", "sk": {"$regex": "UPDA"}})

    def test_iguser_update_length(self, iguser_update):
        assert len(iguser_update) == 7

    def test_iguser_update_retrieved(self, iguser_update):
        assert isinstance(iguser_update["retrieved_at_time"], int)

    def test_iguser_update_sk(self, iguser_update):
        assert len(iguser_update["sk"]) == 30

    def test_iguser_update_username(self, iguser_update):
        assert iguser_update["username"] == "testuser"

    def test_iguser_update_user_id(self, iguser_update):
        assert iguser_update["user_id"] == 12345

    def test_iguser_update_json(self, iguser_update):
        assert iguser_update["json"] == {'biography': 'My Biography', 'edge_followed_by': {'count': 4}}

    @pytest.fixture()
    def iguser_posts(self, write_iguser):
        return list(write_iguser.collection.find({"sk": "POST"}))

    def test_iguser_posts_length(self, iguser_posts):
        assert len(iguser_posts) == 2

    def test_iguser_posts_item_length(self, iguser_posts):
        assert len(iguser_posts[0]) == 4

    def test_iguser_posts_pk(self, iguser_posts):
        assert iguser_posts[0]["pk"] == "PO#XAB"

    def test_iguser_posts_sk(self, iguser_posts):
        assert iguser_posts[0]["sk"] == "POST"

    def test_igusers_posts_discovered_integer(self, iguser_posts):
        assert isinstance(iguser_posts[0]["discovered_at_time"], int)


class TestIGPostMongo:
    @pytest.fixture()
    def igpost(self):
        loader = IGLoader(item=IGPost())
        loader.add_value("shortcode", "BBA")
        loader.add_value("shortcode", "CCA")
        loader.add_value("owner_username", "testuser")
        loader.add_value("owner_id", "12345")
        loader.add_value("id", "56789")
        loader.add_value("retrieved_at_time", "91111")
        loader.add_value("post_json", {"category1": "result1", "category2": "result2"})

        return loader.load_item()

    @pytest.fixture()
    def write_igpost(self, mongodb_pipeline, igpost):
        spider = None
        igpost["images"] = [{"test1": "result1"}]
        mongodb_pipeline.process_item(igpost, spider)
        return mongodb_pipeline

    @pytest.fixture()
    def igpost_main(self, write_igpost):
        return write_igpost.collection.find_one({"pk": "PO#BBA", "sk": {"$regex": "POST"}})

    def test_igpost_main_length(self, igpost_main):
        assert len(igpost_main) == 6

    def test_igpost_main_pk(self, igpost_main):
        assert igpost_main["pk"] == "PO#BBA"

    def test_igpost_main_discovered(self, igpost_main):
        assert igpost_main["discovered_at_time"] == 91111

    def test_igpost_main_retrieved(self, igpost_main):
        assert igpost_main["retrieved_at_time"] == 91111

    def test_igpost_main_images(self, igpost_main):
        assert isinstance(igpost_main["image"], dict)

    @pytest.fixture()
    def igpost_update(self, write_igpost):
        return write_igpost.collection.find_one({"pk": "PO#BBA", "sk": {"$regex": "UPDA"}})

    def test_igpost_update_length(self, igpost_update):
        assert len(igpost_update) == 9

    def test_igpost_update_retrieved(self, igpost_update):
        assert isinstance(igpost_update["retrieved_at_time"], int)

    def test_igpost_update_sk(self, igpost_update):
        assert len(igpost_update["sk"]) == 30

    def test_igpost_update_shortcode(self, igpost_update):
        assert igpost_update["shortcode"] == "BBA"

    def test_igpost_update_username(self, igpost_update):
        assert igpost_update["username"] == "testuser"

    def test_igpost_update_user_id(self, igpost_update):
        assert igpost_update["user_id"] == 12345

    def test_igpost_update_post_id(self, igpost_update):
        assert igpost_update["post_id"] == 56789

    def test_igpost_update_json(self, igpost_update):
        assert igpost_update["json"] == {'category1': 'result1', 'category2': 'result2'}
