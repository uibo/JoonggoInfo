import 'dart:ffi';
import 'dart:io';

import 'package:jginfo_client/jginfo_client.dart';
import 'package:pretty_json/pretty_json.dart';

void main (List<String> arguments) async {
  while (true) {
    print("1) getItems    2) getMal    3) postItem");
    var selectionFunction = stdin.readLineSync();
    switch (selectionFunction) {
      case '1':
      print(prettyJson(await getItems()));
      case '2':
      print(prettyJson(await getMal()));
      case '3':
      print(await postItem());
    }
  } 
}