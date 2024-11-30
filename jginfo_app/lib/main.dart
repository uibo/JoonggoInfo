import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  runApp(MyApp());
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
      home: MainPage()
    );
  }
}

class MainPage extends StatefulWidget {
  const MainPage ({super.key});

  @override
  MainPageState createState() => MainPageState();
}

class MainPageState extends State<MainPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  // @override
  // void initState() {
  //   super.initState();
  //   _pageController = PageController();
  // }
  
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
        leading: Center(
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
              padding: EdgeInsets.symmetric(
                horizontal: 70
              ),
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
              padding: EdgeInsets.symmetric(
                horizontal: 70
              ),
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
              padding: EdgeInsets.symmetric(
                horizontal: 70
              ),
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
        onPageChanged: (index) {
          // setState(() => _currentPage = index);
        },
        children: [
          ChartPage(),
          ListPage(),
          EnrollPage()
        ],
      ),
      backgroundColor: Colors.white
    );
  }
}

class ChartPage extends StatefulWidget {
  const ChartPage ({super.key});

  @override
  ChartPageState createState() => ChartPageState();
}
class ChartPageState extends State<ChartPage> {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SettingBar(),
        Expanded( // 남은 공간 채우기
          child: Text("chart\nchart\nchart\nchart\nchart\nchart\nchart\nchart\nchart\n"), // 그래프 위젯
        ),
      ],
    );
  }
}

class ListPage extends StatelessWidget {
  const ListPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('List Page Content'));
  }
}

class EnrollPage extends StatelessWidget {
  const EnrollPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: Text('Enroll Page Content'));
  }
}

class DropdownButtonTemplate extends StatefulWidget {
  const DropdownButtonTemplate (this.list);
  final List<String>? list;

  @override
  DropdownButtonTemplateState createState() => DropdownButtonTemplateState();
}
class DropdownButtonTemplateState extends State<DropdownButtonTemplate> {
  late List<String>? _list;
  late String _selectedValue;

  @override
  void initState() {
    super.initState();
    _list = widget.list;
    _selectedValue = _list![0];
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 50,
      decoration: ShapeDecoration(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          side: BorderSide(width: 2, color: Color(0xFFB1B9C0)),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      child: DropdownButton(
        underline: Container(),
        focusColor: Colors.white, // 포커스 시 색상
        value: _selectedValue,
        items: _list?.map<DropdownMenuItem<String>>((String value) {
          return DropdownMenuItem<String>(
            value: value,
            child: Text(value.padRight(20)),
          );
        }).toList(),
        onChanged: (String? newValue) {
          setState(() {
            _selectedValue = newValue!;
          });
        },
      ),
    );
  }
}



class SettingBar extends StatelessWidget {
  const SettingBar ({super.key});
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SettingBar1(),
        SettingBar2(),
      ],
    );
  }
}

class SettingBar1 extends StatelessWidget {
  const SettingBar1({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        DropdownButtonTemplate(['iPhone14', 'iPhone15']),
        DropdownButtonTemplate(['Normal', 'Plus']),
        DropdownButtonTemplate(['128GB', '256GB']),
        DatePicker(),
        DatePicker(),
        Container(
          padding: EdgeInsets.only(top:20, bottom: 20),
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              overlayColor: Colors.yellowAccent,
              minimumSize: Size(30, 40),
              backgroundColor: const Color.fromARGB(255, 45, 45, 45),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)
              )
            ),
            onPressed: () {}, 
            child: Text(
              '검색',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontFamily: 'Open Sans',
              ),
            ),
          ),
        )
      ]
    );
  }
}

class DatePicker extends StatefulWidget {
  const DatePicker ({super.key});

  @override
  DatePickerState createState() => DatePickerState();
}
class DatePickerState extends State<DatePicker> {
  DateTime selectedDate = DateTime.now();

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: DateTime(2000),
      lastDate: DateTime(2025),
    );
    
    if (picked != null && picked != selectedDate) {
      setState(() {
        selectedDate = picked;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 50,
      decoration: ShapeDecoration(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          side: BorderSide(width: 2, color: Color(0xFFB1B9C0)),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      child: TextButton(
        onPressed: () => _selectDate(context),
        child: Row(
            children: [
              Text("${selectedDate.toString().split(' ')[0]}",
                style: TextStyle(fontSize: 16)
              ),
              FlutterLogo()
            ]
          ),
      )
    );
  }
}


class SettingBar2 extends StatelessWidget {
  const SettingBar2({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        BatteryWidget(),
        SaleStatusButton2(),
        Row(
          children: [
            OptionButton('기스'),
            OptionButton('흠집'),
            OptionButton('찍힘'),
            OptionButton('파손'),
            OptionButton('잔상'),
            OptionButton('미개봉'),
            OptionButton('애플케어플러스', containerWidth: 150,),
          ],
        ),
      ],
    );
  }
}

class BatteryWidget extends StatefulWidget {
  const BatteryWidget({super.key});

  @override
  State<BatteryWidget> createState() => _BatteryWidgetState();
}
class _BatteryWidgetState extends State<BatteryWidget> {
  int batteryValue = 0;
  
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return 
    Row(
      children: [
        Text(
          "Battery",
          style: TextStyle(
            fontSize: 17,
            fontFamily: 'Inter',
            fontWeight: FontWeight.w500,
          )
        ),
        SizedBox(width: 10,),
        NumberInput(),
      ],
    );
  }
}

class NumberInput extends StatefulWidget {
  const NumberInput({super.key});

  @override
  State<NumberInput> createState() => _NumberInputState();
}
class _NumberInputState extends State<NumberInput> {
  late TextEditingController _controller;
  var _value = 0;
  final min = 0;
  final max = 100;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: _value.toString());
  }

  void _updateValue(int newValue) {
    if (newValue >= min && newValue <= max) {
      setState(() {
        _value = newValue;
        _controller.text = _value.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 150,
      child: Row(
        children: [
          Container(
            decoration: ShapeDecoration(
              shape: RoundedRectangleBorder(
                side: BorderSide(width: 2, color: Color(0xFF7E878F)),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: () => _updateValue(_value - 1),
              icon: Icon(Icons.remove),
            ),
          ),
          Expanded(
            child: TextField(
              controller: _controller,
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              onChanged: (value) {
                if (value.isNotEmpty) {
                  _updateValue(int.parse(value));
                }
              },
              enableInteractiveSelection: false,
            ),
          ),
          Container(
            decoration: ShapeDecoration(
              shape: RoundedRectangleBorder(
                side: BorderSide(width: 2, color: Color(0xFF7E878F)),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: () => _updateValue(_value + 1),
              icon: Icon(Icons.add),
            ),
          ),
        ],
      )
    );
  }
}

enum SaleStatus { sale, sold }
class SaleStatusButton2 extends StatefulWidget {
  const SaleStatusButton2 ({super.key});
  
  @override
  State<SaleStatusButton2> createState() => _SaleStatusButtonState2();
}
class _SaleStatusButtonState2 extends State<SaleStatusButton2> {
  
  Set<SaleStatus> saleStatus = {SaleStatus.sale};
  
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return SegmentedButton<SaleStatus>(
      style: ButtonStyle(
        side: WidgetStatePropertyAll(BorderSide(width: 2)),
        shape: WidgetStatePropertyAll<OutlinedBorder>(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
          ),
        ),
      ),
      segments: const <ButtonSegment<SaleStatus>>[
        ButtonSegment<SaleStatus>(
          value: SaleStatus.sale,
          label: SizedBox(
            width: 70, 
            child: Text("판매중"),
          ),
          icon: Icon(
            Icons.check_box_outline_blank,
          ),
        ),
        ButtonSegment<SaleStatus>(
          value: SaleStatus.sold,
          label: SizedBox(
            width: 70, 
            child: Text("판매완료"),
          ),
          icon: Icon(
            Icons.check_box_outline_blank,
          ),
        ),
      ],
      selected: saleStatus,
      onSelectionChanged: (Set<SaleStatus> newSelection) {
        setState(() {
          saleStatus = newSelection;
        });
      },
      multiSelectionEnabled: true,
      emptySelectionAllowed: true,
    );
  }
}

class SaleStatusButton1 extends StatefulWidget {
  const SaleStatusButton1({super.key});

  @override
  State<SaleStatusButton1> createState() => _SaleStatusButton1State();
}
class _SaleStatusButton1State extends State<SaleStatusButton1> {
  bool selectedSale = false;
  bool selectedSold = false;

  @override
  Widget build(BuildContext contet) {
    return Container(
      width: 240,
      height: 40,
      decoration: ShapeDecoration(
        shape: RoundedRectangleBorder(
          side: BorderSide(width: 2, color: Color(0xFF495057)),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              color: selectedSale == true?Colors.black : Colors.white,
              child: Center(
                child: TextButton(
                  onPressed: () => setState(() {
                    selectedSale = !selectedSale;
                  }),
                  child: Text(
                    '판매중',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: selectedSale == true?Colors.white : Colors.black,
                      fontSize: 16,
                      fontFamily: 'Open Sans',
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            )
          ),
          Container(
            width: 1,
            height: 40,
            color: Colors.black,
          ),
          Expanded(
            child: Container(
              color: selectedSold == true?Colors.black : Colors.white,
              child: Center(
                child: TextButton(
                  onPressed: () => setState(() {
                    selectedSold = !selectedSold;
                  }), 
                  child: Text(
                    '판매완료',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: selectedSold == true?Colors.white : Colors.black,
                      fontSize: 16,
                      fontFamily: 'Open Sans',
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            )
          ),
        ],
      ),
    );
  }
}

class OptionButton extends StatefulWidget {
  const OptionButton (this.optionName, {super.key, this.containerWidth = 80});
  final String optionName;
  final int containerWidth;

  @override
  OptionButtonState createState() => OptionButtonState();
}
class OptionButtonState extends State<OptionButton> {
  bool _selectedState = false;

  void changeState() {
    setState(() {
      _selectedState = !_selectedState;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
        decoration: ShapeDecoration(
          color: _selectedState == false ? Colors.white : Color(0xFF495057),
          shape: RoundedRectangleBorder(
            side: BorderSide(
              width: 2, 
              color: Color(0xFF495057)
            ),
            borderRadius: BorderRadius.circular(6),
          ),
        ),
        child: Center(
          child: TextButton(
            onPressed: changeState,
            child: Text(
              widget.optionName,
              style: TextStyle(
                color:_selectedState == false? Color(0xFF495057) : Colors.white,
                fontSize: 16,
                fontFamily: 'Open Sans',
              ),
            ),
          )
        ),
      );
  }
}




