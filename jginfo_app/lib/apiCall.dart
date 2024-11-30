import 'dart:convert';

import 'package:http/http.dart';

Future<dynamic> getItems() async {
  String model = "iPhone14ProMax";
  String storage = "512GB";
  int? status = null;
  int battery =-1;
  String featList='0000000';
  var url = Uri(scheme: 'http',
                host: '127.0.0.1',
                port: 8000,
                path: '/iPhone14_processed_info',
                queryParameters: {"model": model, 
                                  "storage": storage,
                                  //"status": "$status",
                                  "battery": "$battery", 
                                  "feat_list": featList});
  print(url.queryParameters);
  var res = await get(url);
  return jsonDecode(utf8.decode(res.bodyBytes));
}

Future<List<dynamic>> getMal() async {
  String model = "iPhone14ProMax";
  String storage = "512GB";
  int? status = null;
  int battery =-1;
  String featList='0000000';
  var url = Uri(scheme: 'http',
                host: '127.0.0.1',
                port: 8000,
                path: '/movingaverageline',
                queryParameters: {"model": model, 
                                  "storage": storage,
                                  //"status": "$status",
                                  "battery": "$battery", 
                                  "feat_list": featList});
  var res = await get(url);
  return jsonDecode(utf8.decode(res.bodyBytes));
}

Future<Map> postItem() async {
  Map<String, dynamic> body = {
    "model": "iPhone14MaxPro",
    "storage": "1024GB",
    "battery": -1,
    "upload_date": "2024-11-10",
    "price": 800000,
    "status": 1,
    "location": "하갈동",
    "imgUrl": "https://test.img",
    "url": "http://test.url",
    "feat_list": {"깔끔함": 1}
  };
  var url = Uri(scheme: 'http',
                host: '127.0.0.1',
                port: 8000,
                path: '/iPhone14_processed_info/');
  var res = await post(url, headers: {"Content-Type": "application/json"}, body: jsonEncode(body));
  return jsonDecode(utf8.decode(res.bodyBytes));
}
