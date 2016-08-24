from vis.analyzers.indexers import noterest, interval, new_ngram, meter, dissonance, active_voices
from vis.models.indexed_piece import IndexedPiece 
from vis.models.aggregated_pieces import AggregatedPieces
import pandas
import numpy
import pdb
import time
from vis.analyzers.indexers import lilypond
from vis.analyzers.experimenters.lilypond import PartNotesExperimenter, AnnotateTheNoteExperimenter, \
    LilyPondExperimenter, annotate_the_note

"""Prototype Intervallic-Rhythm Indexer"""

# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Josquin_De_beata_Virgine_Gloria.xml'
# piece_path2 = '/home/amor/Code/vis-framework/vis/tests/corpus/bwv2.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_9_Qui_Vult.xml' # example of changing IR by acceleration
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Josquin_Duets/Crucifixus.xml' #example of IR = half note
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Morley_Duets/7 Miraculous loves wounding.xml' # example of IR = quarter note
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Morley_Duets/1 Goe yee my canzonets.xml' # example of changing IR by slowing down # currently not detected!

# Senfl Pieces:
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/AssumptaEst_normal.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/DumSteteritis_normal.xml'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Senfl_Buchner/No01_Converte_nos Kopie.xml'

pieces = ['/home/amor/Code/vis-framework/vis/tests/corpus/Josquin_De_beata_Virgine_Gloria.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Agnus Dei.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Crucifixus.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Et incarnatus est.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Ad_fugam_Sanctus_version_2_Pleni.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Ad_fugam_Sanctus_version_2_Qui_venit.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Allez_regretz_I_Sanctus_Pleni.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Ave_maris_stella_Sanctus_Benedictus.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Ave_maris_stella_Sanctus_Qui_venit.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Missa_Pange_lingua_Sanctus_Benedictus.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/J_corpus/Qui edunt me.xml',

    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_1_Beatus_Vir.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_2_Beatus_Homo.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_3_Oculus.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_4_justus.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_5_Expectatio.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_6_Qui_Sequitur_Me.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_7_Justi.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_8_Sancti_mei.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_9_Qui_Vult.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_10_Serve_bone.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_11_Fulgebunt_justi.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/L_corpus/Lassus_12_Sicut_Rosa.xml',

    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/1 Goe yee my canzonets.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/2 When loe by break of morning.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/3 Sweet nymph.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/5 I goe before my darling.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/6 La Girandola.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/7 Miraculous loves wounding.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/8 Lo heere another love.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/11 Fyre and Lightning.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/13 Flora wilt thou torment mee.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/15 In nets of golden wyers.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/17 O thou that art so cruell.xml',
    # '/home/amor/Code/vis-framework/vis/scripts/M_corpus/19 I should for griefe and anguish.xml',
    ]
ccr_s, ni_s = [], []
v_setts = {'quality': True, 'simple or compound': 'simple'}
h_setts = {'quality': False, 'simple or compound': 'compound'}
h_setts2 = {'quality': True, 'simple or compound': 'compound', 'horiz_attach_later': True}
n_setts = {'n': 3, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
w = 6 # w is for window
ends = []

for number, piece_path in enumerate(pieces):
    ind_piece = IndexedPiece(piece_path)
    piece = ind_piece._import_score()
    parts = piece.parts
    nr = noterest.NoteRestIndexer(parts).run()
    dr = meter.DurationIndexer(parts).run()
    ms = meter.MeasureIndexer(parts).run()
    bs = meter.NoteBeatStrengthIndexer(parts).run()
    hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
    hz2 = interval.HorizontalIntervalIndexer(nr, h_setts2).run()
    vt = interval.IntervalIndexer(nr, v_setts).run()
    # ng = new_ngram.NewNGramIndexer((vt, hz2), n_setts).run()
    ds = dissonance.DissonanceIndexer([bs, dr, hz, vt]).run()
    av = active_voices.ActiveVoicesIndexer(nr).run()
    av_sa = active_voices.ActiveVoicesIndexer(nr, {'show_all': True}).run()


    voice_dr_means = []
    # Attack-density analysis each voice. The whole-piece analysis is probably what matters most though.
    for x in range(len(nr.columns)):
        mask = nr.iloc[:, x].dropna()
        # The durations of just the notes
        ndr = dr.iloc[:, x].dropna()[mask != 'Rest']
        mean_roll = ndr.rolling(window=w).mean()
        voice_dr_means.append(mean_roll)

    vdm = pandas.concat(voice_dr_means, axis=1)

    # Attack-density analysis for whole piece.
    n_ind = nr[nr != 'Rest'].index
    combined = pandas.Series(n_ind[1:] - n_ind[:-1], index=n_ind[:-1])
    comb_roll = combined.rolling(w).mean()


    #Remove the upper level of the columnar multi-index.
    ddr = dr.copy()
    ddr.columns = range(len(dr.columns))
    dds = ds.copy()
    dds.columns = range(len(ds.columns))
    nnr = nr.copy()
    nnr.columns = range(len(nr.columns))
    bbs = bs.copy()
    bbs.columns = range(len(bs.columns))

    ds_counts = dds.stack().value_counts()

    # Remove weak dissonances
    weaks = ('R', 'D', 'L', 'U', 'E', 'C', 'A')
    indx, cols = numpy.where(ds.isin(weaks))
    for x in reversed(range(len(indx))):
        spot = ddr.iloc[:indx[x], cols[x]].last_valid_index()
        # Add the weak dissonance duration to the note that immediately precedes it.
        ddr.at[spot, cols[x]] += ddr.iat[indx[x], cols[x]]
    # Remove strong dissonances other than suspensions
    strongs = ('Q', 'H')
    indx, cols = numpy.where(ds.isin(strongs))
    for x in reversed(range(len(indx))):
        spot = ddr.iloc[indx[x]+1:, cols[x]].first_valid_index()
        # Add the strong dissonance duration to the note that immediately follows it.
        ddr.iat[indx[x], cols[x]] += ddr.at[spot, cols[x]]
        ddr.at[spot, cols[x]] = float('nan')
        nnr.iat[indx[x], cols[x]] = nnr.at[spot, cols[x]]
        nnr.at[spot, cols[x]] = float('nan')
    # Delete the duration entries of weak dissonances 
    ddr[dds.isin(weaks)] = float('nan')
    nnr[dds.isin(weaks)] = float('nan')
    # Delete the duration entries of strong dissonances other than suspensions
    ddr[dds.isin(strongs)] = float('nan')
    # Delete duration entries for rests
    ddr = ddr[nnr != 'Rest']
    ddr.dropna(how='all', inplace=True)

    # save = ddr.copy()
    # no_rest = nnr[nnr != 'Rest'].copy()
    # # Add agogically weak notes into their preceding agogically strong ones
    # for j in range(len(nnr.columns)):
    #     col = no_rest.iloc[:, j].dropna()
    #     repeats = numpy.where(col == col.shift())[0]
    #     for rep in repeats:
    #         if (ddr.at[col.index[rep], j] < ddr.at[ddr.loc[:col.index[rep - 1], j].last_valid_index(), j] and # the second note is shorter than the first
    #             bbs.at[col.index[rep], j] < bbs.at[bbs.loc[:col.index[rep - 1], j].last_valid_index(), j]): # the second note has a weaker beatstrength than the first
    #             ddr.at[ddr.loc[:col.index[rep -1], j].last_valid_index(), j] += ddr.at[col.index[rep], j]
    #             ddr.at[col.index[rep], j] = float('nan')

    # TODO: remove anticipations of suspension resolutions. Consider various common ornament types.
    # TODO: related to above. Remove all consonant anticipations.
    # TODO: account for repeated notes like m. 116-117 in Josquin Kyrie from Missa Pro defunctus.
    # TODO: require dissonances on a level to confirm that new level **** Pick up here *****
    # TODO: consider temporality by searching for cadential ngrams that coincide with important decreases in attack density
    # TODO: durational breaks by evaluating whether or not the longest duration of any note is equal to
    #       the attack density at that moment.
    # TODO: check to see what the average number of voices is when the IR is faster vs. slower

    voice_ddr_means = []
    # Attack-density analysis each voice without most dissonances. The whole-piece analysis is probably what matters most though.
    for x in range(len(nr.columns)):
        mean_roll = ddr.iloc[:, x].dropna().rolling(window=w).mean()
        voice_ddr_means.append(mean_roll)
    vddm = pandas.concat(voice_ddr_means, axis=1)

    # Attack-density analysis without most dissonances for the whole piece.
    combined2 = pandas.Series(ddr.index[1:] - ddr.index[:-1], index=ddr.index[:-1])
    comb_roll2 = combined2.rolling(w).mean()
    combs = pandas.concat([comb_roll, comb_roll2], axis=1)


    # Broadcast any bs value to all columns of a df.
    cbs = pandas.concat([bs.T.bfill().iloc[0]]*len(bbs.columns), axis=1, ignore_index=True)


    diss_levs = {'4/2w': {.0625: 1, .125: 2, .25: 4, .5: 8, 1: 8}, #NB: for now things that happen on beats 1 and 3 are treated the same way.
                 '4/2s': {.0625: .25, .125: .5, .25: 1, .5: 2, 1: 2},
                 '4/4w': {.0625: .5, .125: 1, .25: 2, .5: 4, 1: 4}, #NB: for now things that happen on beats 1 and 3 are treated the same way.
                 '4/4s': {.0625: .125, .125: .25, .25: .5, .5: 1, 1: 1},
                 }

    # Get the beatstrength of the dissonances
    diss_ir = bbs[dds.isin(weaks)]
    if number < 22:
        diss_ir.replace(diss_levs['4/2w'], inplace=True)
    else:
        diss_ir.replace(diss_levs['4/4w'], inplace=True)

    swsus = ('S', 'Q', 'H')
    sbs = cbs[dds.isin(swsus)]
    if number < 22:
        sbs.replace(diss_levs['4/2s'], inplace=True)
    else:
        sbs.replace(diss_levs['4/4s'], inplace=True)

    # IR analysis based on dissonance types alone.
    diss_ir.update(sbs)

    # Pseudo-code for requiring dissonance confirmation of IR analysis:
    cr = comb_roll2.copy()
    ccr = cr.copy()
    # There's surely a more elegant way to do this, but for now snap the readings to a reasonable note-value grid.
    # .75, 1.5, and 3 are placeholders telling you that the final value should be the next greater or smaller value.
    # Basically this means that the IR reading can only be an eighth, quarter, half, or whole note.
    mlt = 1.25 # top threshhold above which to round IR reading up.
    ccr[cr < .5*mlt] = .5
    ccr[cr > .5*mlt] = 1
    ccr[cr > 1*mlt] = 2
    ccr[cr > 2*mlt] = 4

    for i, val in enumerate(ccr):
        counts = diss_ir.iloc[i:i+w].stack().value_counts()
        lvi = ccr.iloc[:i].last_valid_index()
        if len(counts) > 0 and counts.index[0] == val: # If the most common diss in the window corresponds to the attack-density reading, leave the current val
            continue

        elif lvi is not None and ccr.at[lvi] == val: # There is no dissonance in this window, but the IR analysis has not changed, so the reading is valid
            continue
        else: # The new level has not been confirmed by a corresponding dissonance
            ccr.iat[i] = float('nan')

    ccr.ffill(inplace=True)
    ccr.bfill(inplace=True)
    ccr = ccr.loc[ccr.shift() != ccr] # Remove consecutive duplicates


    spots = list(ccr.index)
    spots.append(nr.index[-1] + dr.iloc[-1].max()) # Add the index value of the last moment of the piece which usually has no event at it.
    new_index = []
    for i, spot in enumerate(spots[:-1]):
        if spot % ccr.iat[i] != 0:
            spot -= (spot % ccr.iat[i])
        post = list(numpy.arange(spot, spots[i+1], ccr.iat[i])) # you can't use range() because range can't handle floats
        if bool(new_index) and bool(post) and post[0] in new_index:
            del post[0]
        new_index.extend(post)

    ccr_s.append(ccr)
    ni_s.append(new_index)
    ends.append(nnr.index[-1])
    print("Analyzed: " + piece_path)

res = pandas.concat(ccr_s, axis=1)
ends = pandas.Series(ends)
J = res.iloc[:, :10].dropna(how='all')
L = res.iloc[:, 10:22].dropna(how='all')
M = res.iloc[:, 22:].dropna(how='all')

pdb.set_trace()

# reindexed = pandas.concat([nnr.iloc[:, x].reindex(new_index).ffill() for x in range(len(nnr.columns))], axis=1)
# ri_hz = interval.HorizontalIntervalIndexer(reindexed, h_setts2).run()
# ri_vt = interval.IntervalIndexer(reindexed, v_setts).run()
# ri_ng = new_ngram.NewNGramIndexer((ri_vt, ri_hz), n_setts).run()


# # # Output to Lilypond
# # setts = {'run_lilypond': True, 'output_pathname': '/home/amor/Code/vis-framework/vis/scripts/Lilypond_Output', 'annotation_part': ri_vt}
# # LilyPondExperimenter([piece], setts).run()


# # TODO: use this new index in the same way that the current offset indexer does

# cads = ng[ng == 'm7 P1 M6 -M2 P8'].dropna(how='all')
# # cads2 = ng[ng == 'M2 -M2 M3 M2 P1'].dropna(how='all')
# # cads3 = ng[ng == 'M2 -M2 M3 M2 M3'].dropna(how='all')
# # print(cads2)
# # print(cads3)

# # Condense cadential ngrams to one series.
# condensed_cads = cads.T.bfill().iloc[0]

# ir_cads = pandas.concat((comb_roll2, condensed_cads), axis=1)
# filtered = pandas.concat((comb_roll2[comb_roll2 > 2.7], condensed_cads), axis=1, ignore_index=True)


# temp = pandas.concat((comb_roll2, av), axis=1, ignore_index=True)
# temp = temp[temp.iloc[:,0] > 2.7]
# f2 = pandas.concat((temp, condensed_cads), axis=1, ignore_index=True)

# pdb.set_trace()

# # t0 = time.time()
# # cads2 = ng[ng == 'M2 -M2 M3 M2 P1'].dropna(how='all')
# # t1 = time.time()
# # print('Runtime: ' + str(t1-t0))




# # ### This works but is problematic for two-voice pieces that often momentarily drop to 1 active voice.
# # # Combine av and ms dfs.
# # cb_av = pandas.concat((combined2, av), axis=1, ignore_index=True)
# # # Figure out where there are zero or one active voices in all events but the one at the last index. lt2 stands for "less than two".
# # temp = list(numpy.where(cb_av.iloc[:-1, 1] < 2)[0])
# # temp.insert(0, -1) # add a -1 placeholder at the beginning
# # temp.append(len(cb_av.index)) # also add a placeholder at the end to frame the slices correctly
# # tups = zip(temp, temp[1:])
# # lt2 = filter(lambda a: a[1]-a[0] > 1, tups)
# # # get rolling averages for all chunks of the piece that have a continuous stream of at least two voices.
# # chunks = [cb_av.iloc[x[0]+1:x[1]-1, 0].dropna().rolling(w).mean() for x in lt2]
# # whole = pandas.concat(chunks)
# # res = pandas.concat((comb_roll2, whole), axis=1)

# # downbeats = cbs[cbs == 1].dropna(how='all')
