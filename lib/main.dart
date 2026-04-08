import 'dart:ffi';

import 'package:firebase_database/firebase_database.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart'; // For dynamic loading GIF
import 'package:animated_text_kit/animated_text_kit.dart'; // For animated text

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Call Fraud Detection AI Agent',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  late FlutterTts flutterTts;
  double volume = 0.5;
  double pitch = 1.0;
  double rate = 0.5;
  Color _color = Color(0xFFD6D6D6);
  final DatabaseReference ref = FirebaseDatabase.instance.ref();
  String _speakValue = "OK";
  String _resourceValue = "Loading...";
  bool isSpeaking = false;
  bool callInSession = true;
  String _title = "Decision Pending...";
  bool _isPause = false;
  @override
  void initState() {
    super.initState();
    initTts();
    _listenForResourceChanges();
  }

  @override
  void dispose() {
    super.dispose();
    flutterTts.stop();
  }

  void _listenForResourceChanges() {
    ref.child('Response').onValue.listen((DatabaseEvent event) {
      if (event.snapshot.exists) {
        setState(() {
          _color = Color(0xFFFFE4B5);
          // Light golden color during speaking
          _speakValue = extractActionText(event.snapshot.value.toString());
          _title = extractDecisionText(event.snapshot.value.toString());

          _resourceValue = extractReasoningAndAction(event.snapshot.value.toString());
          _speak();
        });
      } else {
        setState(() {
          _speakValue = "OK";
        });
      }
    });
  }

  dynamic initTts() {
    flutterTts = FlutterTts();
    flutterTts.setCompletionHandler(() {
      setState(() {
        isSpeaking = false;
        _color = Color(0xFFADD8E6);  // Light blue denoting ongoing call
      });
      print('Speech synthesis completed');
    });

    flutterTts.setErrorHandler((message) {
      print('Error occurred: $message');
    });
    _setAwaitOptions();
  }

  Future<void> _speak() async {
    if (_speakValue.isNotEmpty && _speakValue != "OK") {
      setState(() {
        isSpeaking = true;
      });
      await flutterTts.speak(_speakValue);
    }
  }

  Future<void> _setAwaitOptions() async {
    await flutterTts.awaitSpeakCompletion(true);
  }

  void _endCall() {
    flutterTts.pause();
    setState(() {
      callInSession = false;
      _color = Colors.grey[300]!;  // Color denoting ended call
      isSpeaking = false;
    });
  }

  void _pause() {
    flutterTts.pause();
    setState(() {
      _isPause = true;
      isSpeaking = false;
      _color = Color(0xFFADD8E6);  // Light blue color denoting ongoing call
    });
  }

  String extractActionText(String inputText) {
    String actionMarker = "Action:";
    int actionStartIndex = inputText.indexOf(actionMarker);
    if (actionStartIndex != -1) {
      return "Please" + inputText.substring(actionStartIndex + actionMarker.length).trim() +". More information can be viewed in the app";
    }

    return "OK";
  }
  String extractDecisionText(String inputText) {
    String decisionMarker = "Decision:";
    int decisionStartIndex = inputText.indexOf(decisionMarker);
    if (decisionStartIndex != -1) {
      int decisionEndIndex = inputText.indexOf('\n', decisionStartIndex);
      return inputText.substring(decisionStartIndex + decisionMarker.length, decisionEndIndex).trim().toUpperCase();;
    }

    return "Decision Pending...";
  }

  String extractReasoningAndAction(String inputText) {
    String reasoningMarker = "Reasoning:";
    String actionMarker = "Action:";

    int reasoningStartIndex = inputText.indexOf(reasoningMarker);
    int actionStartIndex = inputText.indexOf(actionMarker);

    String reasoningText = "";
    String actionText = "";

    if (reasoningStartIndex != -1) {
      int reasoningEndIndex = actionStartIndex != -1 ? actionStartIndex : inputText.length;
      reasoningText = inputText.substring(reasoningStartIndex + reasoningMarker.length, reasoningEndIndex).trim();
    }

    if (actionStartIndex != -1) {
      actionText = inputText.substring(actionStartIndex + actionMarker.length).trim();
    }

    return 'Reasoning: $reasoningText\n\nAction: $actionText';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Call Cop'),
            if (callInSession)
              Row(
                children: [
                  Icon(Icons.call),
                  SizedBox(width: 8),
                  DefaultTextStyle(
                    style: const TextStyle(
                      fontSize: 20.0,
                      color: Colors.white,
                    ),
                    child: AnimatedTextKit(
                      animatedTexts: [
                        _isPause? TypewriterAnimatedText("AI Not Listening..."): TypewriterAnimatedText('In Session...'),
                      ],
                      repeatForever: true,
                    ),
                  ),
                ],
              ),
            if (!callInSession)
              Row(
                children: [
                  Icon(Icons.call_end),
                  SizedBox(width: 8),
                  Text('Call Ended'),
                ],
              ),
          ],
        ),
        backgroundColor: callInSession ? Colors.blue : Colors.grey,
        actions: [
          IconButton(
            icon: Icon(Icons.more_vert),
            onPressed: () {
              // Action for more options
            },
          ),
        ],
      ),
      backgroundColor: _color,
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            // Logo Area
            Expanded(
              flex: 2,
              child: Center(
                child: Image.asset('images/logo2.png'),
              ),
            ),
            // Padding between logo and spinner
            SizedBox(height: 20),
            // SpinKitWave GIF
            if (isSpeaking)
              Center(
                child: SpinKitWave(
                  color: Colors.black,
                  size: 50.0,
                ),
              ),
            // Padding between spinner and text box
            SizedBox(height: 20),
            Container(
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 4,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: Text(
                _title,
                style: TextStyle(
                  color: Colors.red,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            // Padding between title and text box
            SizedBox(height: 20),            // Text Alert Box
            Expanded(
              flex: 3,
              child: SingleChildScrollView(
                child: Container(
                  padding: EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 4,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: AnimatedTextKit(
                    animatedTexts: [
                      ColorizeAnimatedText(
                        _resourceValue,
                        textStyle: TextStyle(
                          fontSize: 24.0,
                          fontWeight: FontWeight.bold,
                        ),
                        colors: [
                          Colors.red,
                          Colors.redAccent
                        ],
                        textAlign: TextAlign.center,
                      ),
                    ],
                    isRepeatingAnimation: true,
                    repeatForever: true,
                  ),
                ),
              ),
            ),
            // Control Buttons
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton.icon(
                    onPressed: _endCall,
                    icon: Icon(Icons.call_end),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    label: Text('End Call'),
                  ),
                  ElevatedButton.icon(
                    onPressed: _pause,
                    icon: Icon(Icons.pause),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isPause? Colors.grey: Colors.orange,
                    ),
                    label: Text('Pause'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}