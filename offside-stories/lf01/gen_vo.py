import json,subprocess,os,soundfile as sf,sys
os.environ['HYPERFRAMES_PYTHON']='/home/user/offside-stories/.venv/bin/python'
exec(open('lines.py').read())
only=set(int(x) for x in sys.argv[1:])
S=[];t=0.6
for i,(b,show,say,gap) in enumerate(L):
    raw=f'vo/r{i:03d}.wav'; out=f'vo/p{i:03d}.wav'
    if (not os.path.exists(out)) or i in only:
        subprocess.run(['node','/home/user/portfolio/.claude/skills/hyperframes/scripts/plugin-cli.mjs','tts',say or show,'-v','bm_george','-s','1.02','-o',raw],capture_output=True)
        subprocess.run(['ffmpeg','-v','error','-y','-i',raw,'-af','silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.04','-ar','24000',out])
    d=round(sf.info(out).duration,3)
    S.append(dict(beat=b,show=show,say=say or show,start=round(t,3),dur=d,gap=gap)); t+=d+gap
    print(i,b,round(t,1),flush=True)
json.dump(S,open('vo/script.json','w'),indent=1,ensure_ascii=False)
print('END',round(t,2))
