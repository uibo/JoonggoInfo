import 'package:flutter/material.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'chart_page.dart'; 
import 'list_page.dart'; 
import 'enroll_page.dart'; 

void main() {
  runApp(
    const ProviderScope(
      child: MyApp()
    )
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JGINFO',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.grey),
      ),
      home: const MainPage()
    );
  }
}

class MainPage extends StatefulWidget {
  const MainPage ({super.key});

  @override
  MainPageState createState() => MainPageState();
}

class MainPageState extends State<MainPage> {
  late PageController _pageController;
  int _currentPage = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }
  
  void _goToPage(int index) {
    _pageController.jumpToPage(index);
    setState(() {
      _currentPage = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leadingWidth: 100,
        leading: const Center(
          child: Text(
            'JGINFO',
            style: TextStyle(
              fontSize: 20,
              fontFamily: 'Inter',
              fontWeight: FontWeight.w900,
            ),
          ),
        ),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 70),
              child: TextButton(
                onPressed: () => _goToPage(0),
                style: TextButton.styleFrom(
                  overlayColor: Colors.transparent
                ),
                child: Text(
                  'Chart',
                  style: TextStyle(
                    fontSize: 17,
                    fontFamily: 'Inter',
                    fontWeight: _currentPage == 0 ? FontWeight.bold : FontWeight.normal,
                  )
                ),
              )
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 70),
              child: TextButton(
                onPressed: () => _goToPage(1), 
                style: TextButton.styleFrom(
                  overlayColor: Colors.transparent
                ),
                child: Text(
                  'List',
                  style: TextStyle(
                    fontSize: 17,
                    fontFamily: 'Inter',
                    fontWeight: _currentPage == 1 ? FontWeight.bold : FontWeight.normal,
                  )
                ),
              )
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 70),
              child: TextButton(
                onPressed: () => _goToPage(2), 
                style: TextButton.styleFrom(
                  overlayColor: Colors.transparent
                ),
                child: Text(
                  'Enroll',
                  style: TextStyle(
                    fontSize: 17,
                    fontFamily: 'Inter',
                    fontWeight: _currentPage == 2 ? FontWeight.bold : FontWeight.normal,
                  )
                ),
              )
            ),
          ],
        ),
        centerTitle: true,
      ),
      body: PageView(
        controller: _pageController,
        children: const <Widget>[
          ChartPage(),
          ListPage(),
          EnrollPage()
        ],
      ),
      backgroundColor: Colors.white
    );
  }
}