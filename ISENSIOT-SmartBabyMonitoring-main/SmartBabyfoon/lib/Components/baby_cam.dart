import 'dart:io';
import 'package:audioplayers/audioplayers.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_sound/flutter_sound.dart' hide PlayerState;
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:lecle_yoyo_player/lecle_yoyo_player.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:smart_babyfoon/Components/Widgets/header.dart';

class BabyCam extends StatefulWidget {
  const BabyCam({super.key});

  @override
  State<BabyCam> createState() => _BabyCamState();
}

class _BabyCamState extends State<BabyCam> {
  final db = FirebaseFirestore.instance;

  final soundFile = FirebaseStorage.instance.ref().child('audio');

  bool _mRecorderIsInited = false;
  FlutterSoundRecorder? _myRecorder = FlutterSoundRecorder();

  final player = AudioPlayer();
  bool playerHasSound = false;
  File audioFile = File('');
  Duration duration = Duration.zero;
  Duration position = Duration.zero;
  bool isPlaying = false;

  final uploadSnackBar = const SnackBar(
    backgroundColor: Colors.blue,
    content: Text('Uploading...'),
  );

  final successSnackBar = const SnackBar(
    backgroundColor: Colors.green,
    content: Text('Success'),
  );

  final failedSnackBar = const SnackBar(
    backgroundColor: Colors.red,
    content: Text('Something went wrong'),
  );

  final deleteSnackBar = const SnackBar(
    backgroundColor: Colors.red,
    content: Text('Deleted'),
  );

  Future<void> uploadFile() async {
    final tempDir = await getTemporaryDirectory();
    final file = File('${tempDir.path}/audio');
    ScaffoldMessenger.of(context).showSnackBar(uploadSnackBar);

    soundFile.putFile(file).then((value) {
      ScaffoldMessenger.of(context).clearSnackBars();
      db.collection('sound').doc('playSound').set({
        'playSound': true
      }).then((value) {
        ScaffoldMessenger.of(context).showSnackBar(successSnackBar);
        setState(() {
          audioFile = File('');
          playerHasSound = false;
        });
      }).catchError((error) {
        ScaffoldMessenger.of(context).showSnackBar(failedSnackBar);
      });
    });
  }

  Future<void> record() async {
    if(!_mRecorderIsInited) return;
    audioFile= File('');
    playerHasSound = false;
    final tempDir = await getTemporaryDirectory();

    await _myRecorder!.startRecorder(toFile: '${tempDir.path}/audio');
    setState(() {});
  }

  Future<void> stopRecorder() async {
    final record = await _myRecorder!.stopRecorder();

    audioFile = File(record!);
    setState(() {playerHasSound = true;});
    player.play(UrlSource(audioFile.path));
    player.pause();
  }

  Future<void> initRecorder() async {
    final status = await Permission.microphone.request();
    if(status != PermissionStatus.granted) {
      throw RecordingPermissionException('Microphone permission not granted');
    }

    await _myRecorder!.openRecorder();
    _mRecorderIsInited = true;
  }

  @override
  void initState() {
    super.initState();
    initRecorder();

    player.onPlayerStateChanged.listen((event) {
      setState(() {
        isPlaying = player.state == PlayerState.playing;
      });
    });

    player.onDurationChanged.listen((newDuration) {
      setState(() {
        duration = newDuration;
      });
    });

    player.onPositionChanged.listen((newPosition) {
      setState(() {
        position = newPosition;
      });
    });
  }

  @override
  void dispose(){
    _myRecorder!.closeRecorder();
    _myRecorder = null;

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(
              height: 210,
              child: Header()
            ),
            const Card(
              child: YoYoPlayer(
                url: 'https://livepeercdn.studio/hls/bf490h7w5brdr85k/index.m3u8',
                aspectRatio: 7/8,
                videoStyle: VideoStyle(
                  showLiveDirectButton: true,
                ),
              )
            ),
            IconButton(
              icon: FaIcon(
                _myRecorder!.isRecording ? FontAwesomeIcons.stop: FontAwesomeIcons.microphone,
                size: 30,
                color: const Color(0xff6070ff),
              ),
              onPressed: _myRecorder!.isRecording ? stopRecorder : record,
            ),
            playerHasSound? Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    IconButton(
                      icon: FaIcon(
                        color: const Color(0xff6070ff),
                        isPlaying? FontAwesomeIcons.pause: FontAwesomeIcons.play,
                        size: 30,
                      ),
                      onPressed: () async {
                        if (isPlaying) {
                          await player.pause();
                        } else {
                          await player.play(UrlSource(audioFile.path));
                        }
                      }
                    ),
                    Slider(
                      value: position.inSeconds.toDouble(),
                      onChanged: (value) async {
                        await player.seek(Duration(seconds: value.toInt()));
                      },
                      min: 0,
                      max: duration.inSeconds.toDouble(),
                      activeColor: const Color(0xff6070ff),
                    ),
                    Text(position.toString().split('.').first),
                    const Text(' / '),
                    Text(duration.toString().split('.').first)
                  ],
                ),
                Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      TextButton(
                        onPressed: () {
                          setState(() {
                            audioFile = File('');
                            playerHasSound = false;
                          });
                          ScaffoldMessenger.of(context).showSnackBar(deleteSnackBar);
                        },
                        style: TextButton.styleFrom(
                          backgroundColor: const Color(0xffff0000),
                        ),
                        child: const Text(
                          'Delete',
                          style: TextStyle(
                              color: Colors.white
                          ),
                        ),
                      ),
                      TextButton(
                        onPressed: uploadFile,
                        style: TextButton.styleFrom(
                          backgroundColor: const Color(0xff6070ff),
                        ),
                        child: const Text(
                          'Upload',
                          style: TextStyle(
                            color: Colors.white
                          ),
                        ),
                      ),
                    ],
                  ),
                )
              ],
            ) : Container(),
          ],
        ),
      ),
    );
  }
}