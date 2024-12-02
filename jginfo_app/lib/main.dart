import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

void main() {
  runApp(
    ProviderScope(
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


enum SaleStatus { selling, soldout }
final settingsProvider = StateNotifierProvider<SettingsNotifier, Settings>((ref) => SettingsNotifier());
class SettingsNotifier extends StateNotifier<Settings> {
  SettingsNotifier() : super(Settings(
    toDate: DateFormat("yyyy-MM-dd").format(DateTime.now())));

  void updateproduct (String newValue) {
    state = Settings(
      product: newValue, 
      model: state.model, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatemodel (String newValue) {
    state = Settings(
      product: state.product, 
      model: newValue, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatestorage (String newValue) {
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: newValue,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatefromDate (String newValue) {
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: state.storage,
      fromDate: newValue,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatetoDate (String newValue) {
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: newValue,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatebattery (String newValue) {
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: newValue,
      saleStatus: state.saleStatus,
      options: state.options,
    );
  }
  void updatesaleStatus (Set<SaleStatus> newValue) {
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: newValue,
      options: state.options,
    );
  }
  void updateoption(String key) {
    Map<String, bool> newoptions = Map<String, bool>.from(state.options);

    newoptions[key] = !(newoptions[key] ?? false);
    
    state = Settings(
      product: state.product, 
      model: state.model, 
      storage: state.storage,
      fromDate: state.fromDate,
      toDate: state.toDate,
      battery: state.battery,
      saleStatus: state.saleStatus,
      options: newoptions,
    );
  }
}
class Settings {
  final String product;
  final String model;
  final String storage;
  final String fromDate;
  final String toDate;
  final String battery;
  final Set<SaleStatus> saleStatus; 
  Map<String, bool> options;

  Settings({
    this.product='iPhone14',
    this.model='Normal',
    this.storage='128GB',
    this.fromDate='2022-01-01',
    this.toDate='2024-06-31',
    this.battery='0',
    this.saleStatus=const <SaleStatus>{SaleStatus.selling},
    this.options = const {'기스':false, '흠집':false, '파손':false, '찍힘':false, '잔상':false, '미개봉':false, '애플케어플러스':false}
  });
}

class ChartPage extends ConsumerStatefulWidget {
  const ChartPage ({super.key});

  @override
  ChartPageState createState() => ChartPageState();
}
class ChartPageState extends ConsumerState<ChartPage> {
  @override
  Widget build(BuildContext context) {
    final selectedSettings = ref.watch(settingsProvider);

    return Column(
      children: [
        const SettingBar(),
        Expanded(
          child: Column(
            children: [
              Text(selectedSettings.product),
              Text(selectedSettings.model),
              Text(selectedSettings.storage),
              Text(selectedSettings.fromDate),
              Text(selectedSettings.toDate),
              Text(selectedSettings.battery),
              Text(selectedSettings.saleStatus.toString()),
              Text(selectedSettings.options.toString()),
            ],
          ) 
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

class DropdownButtonTemplate extends ConsumerStatefulWidget {
  const DropdownButtonTemplate ({required this.list, required this.valueName, super.key});
  final List<String> list;
  final String valueName;

  @override
  DropdownButtonTemplateState createState() => DropdownButtonTemplateState();
}
class DropdownButtonTemplateState extends ConsumerState<DropdownButtonTemplate> {
  late List<String> _list;
  late String _valueName;

  @override
  void initState() {
    super.initState();
    _list = widget.list;
    _valueName = widget.valueName;
  }

  @override
  Widget build(BuildContext context) {
    final String selectedValue = ref.watch(settingsProvider.select((settings) {
      switch (_valueName) {
        case 'product': return settings.product;
        case 'model':return settings.model;
        case 'storage': return settings.storage;
        default: return '';
      }
    }));

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
        value: selectedValue,
        items: _list.map<DropdownMenuItem<String>>((String value) {
          return DropdownMenuItem<String>(
            value: value,
            child: Text(value.padRight(20)),
          );
        }).toList(),
        onChanged: (String? newValue) {
          switch (_valueName) {
            case 'product': ref.read(settingsProvider.notifier).updateproduct(newValue!);
            case 'model': ref.read(settingsProvider.notifier).updatemodel(newValue!);
            case 'storage': ref.read(settingsProvider.notifier).updatestorage(newValue!);
          }
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
        Row(
          children: [
            const Expanded(
              child: SettingBar1(),
            ),
            Container(
              margin: const EdgeInsets.only(right: 50),
              padding: const EdgeInsets.only(top:20, bottom: 20),
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  elevation: 2,
                  shadowColor: Colors.lightBlue,
                  enableFeedback: true,
                  overlayColor: Colors.lightBlue,
                  minimumSize: const Size(30, 40),
                  backgroundColor: const Color.fromARGB(255, 45, 45, 45),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)
                  )
                ),
                onPressed: () {}, 
                child: const Text(
                  '검색',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontFamily: 'Open Sans',
                  ),
                ),
              ),
            ),
          ],
        ),
        const SettingBar2(),
      ],
    );
  }
}

class SettingBar1 extends StatelessWidget {
  const SettingBar1({super.key});

  @override
  Widget build(BuildContext context) {
    return const Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        DropdownButtonTemplate(list: ['iPhone14', 'iPhone15'], valueName: 'product',),
        DropdownButtonTemplate(list: ['Normal', 'Plus'], valueName: 'model',),
        DropdownButtonTemplate(list: ['128GB', '256GB'], valueName: 'storage',),
        DatePicker(to: false),
        DatePicker(to: true),
      ]
    );
  }
}

class DatePicker extends ConsumerStatefulWidget {
  const DatePicker ({required this.to, super.key});
  final bool to;

  @override
  DatePickerState createState() => DatePickerState();
}
class DatePickerState extends ConsumerState<DatePicker> {
  late bool _to;
  
  @override
  void initState() {
    super.initState();
    _to = widget.to;
  }

  Future<void> _selectDate(BuildContext context, String selectedDate) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.parse(selectedDate),
      firstDate: DateTime(2020),
      lastDate: DateTime(2025),
    );
    if (picked != null) {
      if (_to) {ref.read(settingsProvider.notifier).updatetoDate(DateFormat('yyyy-MM-dd').format(picked));}
      else {ref.read(settingsProvider.notifier).updatefromDate(DateFormat('yyyy-MM-dd').format(picked));}
    }
  }

  @override
  Widget build(BuildContext context) {
    final String selectedDate = 
      _to == true ? 
      ref.watch(settingsProvider.select((settings) => settings.toDate)) :
      ref.watch(settingsProvider.select((settings) => settings.fromDate));

    return Container(
      height: 50,
      decoration: ShapeDecoration(
        color: Colors.white,
        shape: RoundedRectangleBorder(
          side: const BorderSide(width: 2, color: Color(0xFFB1B9C0)),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      child: TextButton(
        onPressed: () => _selectDate(context, selectedDate),
        child: Row(
            children: [
              Text(
                selectedDate,
                style: const TextStyle(fontSize: 16)
              ),
              const Icon(Icons.calendar_month_sharp)
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
    return const Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        BatteryWidget(),
        SaleStatusButton2(),
        Row(
          children: [
            OptionButton(optionName: '기스', containerWidth: 80,),
            OptionButton(optionName: '흠집', containerWidth: 80,),
            OptionButton(optionName: '파손', containerWidth: 80,),
            OptionButton(optionName: '찍힘', containerWidth: 80,),
            OptionButton(optionName: '잔상', containerWidth: 80,),
            OptionButton(optionName: '미개봉', containerWidth: 80,),
            OptionButton(optionName: '애플케어플러스', containerWidth: 150,),
          ],
        ),
      ],
    );
  }
}

class BatteryWidget extends StatefulWidget {
  const BatteryWidget({super.key});

  @override
  BatteryWidgetState createState() => BatteryWidgetState();
}
class BatteryWidgetState extends State<BatteryWidget> {
  @override
  Widget build(BuildContext context) {
    return 
    const Row(
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

class NumberInput extends ConsumerStatefulWidget {
  const NumberInput({super.key});

  @override
  NumberInputState createState() => NumberInputState();
}
class NumberInputState extends ConsumerState<NumberInput> {
  late TextEditingController _controller;
  final min = 0;
  final max = 100;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void updateValue(int newValue) {
    if (min <= newValue && newValue <= max) {
      ref.read(settingsProvider.notifier).updatebattery(newValue.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final batteryValue = ref.watch(settingsProvider.select((settings) => int.parse(settings.battery)));
    
    if (_controller.text != batteryValue.toString()) _controller.text = batteryValue.toString();

    return Container(
      width: 150,
      child: Row(
        children: [
          Container(
            decoration: ShapeDecoration(
              shape: RoundedRectangleBorder(
                side: const BorderSide(width: 2, color: Color(0xFF7E878F)),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: () => updateValue(batteryValue - 1),
              icon: const Icon(Icons.remove),
            ),
          ),
          Expanded(
            child: TextField(
              controller: _controller,
              textAlign: TextAlign.center,
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              onChanged: (newvalue) {
                if (newvalue.isNotEmpty) {
                  updateValue(int.parse(newvalue));
                }
              },
              enableInteractiveSelection: false,
            ),
          ),
          Container(
            decoration: ShapeDecoration(
              shape: RoundedRectangleBorder(
                side: const BorderSide(width: 2, color: Color(0xFF7E878F)),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            child: IconButton(
              padding: EdgeInsets.zero,
              onPressed: () => updateValue(batteryValue + 1),
              icon: const Icon(Icons.add),
            ),
          ),
        ],
      )
    );
  }
}

class SaleStatusButton2 extends ConsumerStatefulWidget {
  const SaleStatusButton2 ({super.key});
  
  @override
  SaleStatusButtonState2 createState() => SaleStatusButtonState2();
}
class SaleStatusButtonState2 extends ConsumerState<SaleStatusButton2> {
  @override
  Widget build(BuildContext context) {
    Set<SaleStatus> saleStatus = ref.watch(settingsProvider.select((settings) => settings.saleStatus));

    return SegmentedButton<SaleStatus>(
      style: ButtonStyle(
        side: const WidgetStatePropertyAll(BorderSide(width: 2)),
        shape: WidgetStatePropertyAll<OutlinedBorder>(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
          ),
        ),
      ),
      segments: const <ButtonSegment<SaleStatus>>[
        ButtonSegment<SaleStatus>(
          value: SaleStatus.selling,
          label: SizedBox(
            width: 70, 
            child: Text("판매중"),
          ),
          icon: Icon(
            Icons.check_box_outline_blank,
          ),
        ),
        ButtonSegment<SaleStatus>(
          value: SaleStatus.soldout,
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
        ref.read(settingsProvider.notifier).updatesaleStatus(newSelection);
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

class OptionButton extends ConsumerStatefulWidget {
  const OptionButton ({required this.optionName, required this.containerWidth, super.key});
  final String optionName;
  final int containerWidth;

  @override
  OptionButtonState createState() => OptionButtonState();
}
class OptionButtonState extends ConsumerState<OptionButton> {
  @override
  Widget build(BuildContext context) {
    bool selectedState = ref.watch(settingsProvider.select((settings) => settings.options[widget.optionName]!));

    return OutlinedButton(
      onPressed: () {
        ref.read(settingsProvider.notifier).updateoption(widget.optionName);
      },
      style: OutlinedButton.styleFrom(
        foregroundColor: selectedState ? Colors.white : const Color(0xFF495057),
        backgroundColor: selectedState ? const Color(0xFF495057) : Colors.white,
        side: const BorderSide(
          width: 2,
          color: Color(0xFF495057),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      child: Text(
        widget.optionName,
        style: const TextStyle(
          fontSize: 16,
          fontFamily: 'Open Sans',
        ),
      ),
    );
  }
}




